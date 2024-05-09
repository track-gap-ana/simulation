import os
import os.path
from datetime import datetime
import icecube

from icecube import icetray, dataclasses, simclasses, dataio
import icecube.icetray
import icecube.dataclasses
import icecube.dataio
import icecube.phys_services

from icecube.simprod.util import ReadI3Summary, WriteI3Summary
from icecube.simprod.util import CombineHits, DrivingTime, SetGPUEnvironmentVariables

from icecube.icetray import I3Tray, I3Units
from icecube.simprod.util import BasicCounter
from icecube.simprod.segments import GenerateCosmicRayMuons, GenerateNaturalRateMuons, PPC

from icecube.dataclasses import *
from icecube import clsim
from icecube import polyplopia
from icecube import PROPOSAL
from .PropagateMuonsLLP import PropagateMuonsLLP
from icecube.icetray import I3Frame
from icecube.simprod import segments
from icecube import phys_services
from icecube import sim_services
from icecube import vuvuzela
from icecube import DOMLauncher
from icecube import trigger_sim

from icecube.production_histograms import ProductionHistogramModule
from icecube.production_histograms.histogram_modules.simulation.pmt_response import PMTResponseModule
from icecube.production_histograms.histogram_modules.simulation.dom_mainboard_response import InIceResponseModule
from icecube.production_histograms.histogram_modules.simulation.trigger import TriggerModule
from icecube.production_histograms.histograms.simulation.noise_occupancy import NoiseOccupancy
from icecube.production_histograms.histogram_modules.simulation.mctree_primary import I3MCTreePrimaryModule
from icecube.production_histograms.histogram_modules.simulation.mctree import I3MCTreeModule
from icecube.production_histograms.histogram_modules.simulation.mcpe_module import I3MCPEModule


def configure_tray(tray, params, stats, logger):
    """
    Configures the I3Tray instance: adds modules, segments, services, etc.

    Args:
        tray (I3Tray): the IceProd tray instance
        params (dict): command-line arguments (and default values)
                            referenced as dict entries; see add_args()
        stats (dict): dictionary that collects run-time stats
        logger (logging.Logger): the logger for this script
    """
    if params['gpu'] is not None and params['usegpus']:
        SetGPUEnvironmentVariables(params['gpu'])

    tray.AddModule("I3InfiniteSource", "TheSource",
                   Prefix=params['gcdfile'],
                   Stream=icecube.icetray.I3Frame.DAQ)

    ### MUONS WITH MUONGUN ###
    if params['natural_rate']:
        tray.AddSegment(GenerateNaturalRateMuons, "muongun",
                        NumEvents=1e15,
                        mctree_name="I3MCTree_preMuonProp",
                        flux_model="GaisserH4a_atmod12_SIBYLL")
    else:
        # Configure tray segment that actually does stuff.
        tray.AddSegment(GenerateCosmicRayMuons, "muongun",
                        mctree_name="I3MCTree_preMuonProp",
                        num_events=1e15,
                        flux_model=params['model'],
                        gamma_index=params['gamma'],
                        energy_offset=params['offset'],
                        energy_min=params['emin'],
                        energy_max=params['emax'],
                        cylinder_length=params['length'],
                        cylinder_radius=params['radius'],
                        cylinder_x=params['x'],
                        cylinder_y=params['y'],
                        cylinder_z=params['z'],
                        inner_cylinder_length=params['length_dc'],
                        inner_cylinder_radius=params['radius_dc'],
                        inner_cylinder_x=params['x_dc'],
                        inner_cylinder_y=params['y_dc'],
                        inner_cylinder_z=params['z_dc'],
                        use_inner_cylinder=params['deepcore'])

    ### PROPOSAL WITH LLP INTERACTION ###
    if params["propagatemuons"]:
        tray.AddSegment(PropagateMuonsLLP,
                        "propagator",
                        RandomService          = tray.context["I3RandomService"],
                        InputMCTreeName        = "I3MCTree_preMuonProp",
                        OutputMCTreeName       = "I3MCTree",
                        PROPOSAL_config_SM     = params["config_SM"],
                        PROPOSAL_config_LLP    = params["config_LLP"],
                        OnlySaveLLPEvents      = params["OnlySaveLLPEvents"],
                        only_one_LLP           = params["only_one_LLP"],
                        nevents                = params["nevents"],
                        gcdfile                = params["gcdfile"],
                        both_prod_decay_inside = params["both_prod_decay_inside"],
                        min_LLP_length         = params["min_LLP_length"],
                        entry_margin           = params["entry_margin"],
                        exit_margin            = params["exit_margin"],
                    )

    
    if params["use-clsim"]:
        ### PHOTONS WITH CLSIM ###
        tray.AddSegment(clsim.I3CLSimMakeHits, "makeCLSimHits",
                        GCDFile=params['gcdfile'],
                        RandomService=tray.context["I3RandomService"],
                        UseGPUs=params['usegpus'],
                        UseOnlyDeviceNumber=params['useonlydevicenumber'],
                        UseCPUs=not params['usegpus'],
                        IceModelLocation=os.path.join(params['icemodellocation'], params['icemodel']),
                        DOMEfficiency=params['efficiency'],
                        UseGeant4=False,
                        DOMOversizeFactor=params['oversize'],
                        MCTreeName="I3MCTree",
                        MCPESeriesName=params['photonseriesname'],
                        PhotonSeriesName=params['rawphotonseriesname'],
                        HoleIceParameterization=params['holeiceparametrization'])
    else:
        ### PHOTONS WITH PPC
        tray.AddSegment(segments.PPC.PPCTraySegment, "ppc_photons",
                        GPU=params['gpu'],
                        UseGPUs=params['usegpus'],
                        DOMEfficiency=params['efficiency'],
                        DOMOversizeFactor=params['oversize'],
                        IceModelLocation=params['icemodellocation'],
                        HoleIceParameterization=params['holeiceparametrization'],
                        IceModel=params['icemodel'],
                        volumecyl=params['volumecyl'],
                        gpulib=params['gpulib'],
                        InputMCTree=params['mctreename'],
                        keep_empty_events=params['keepemptyevents'],
                        MCPESeriesName=params['photonseriesname'],
                        tempdir=params['tempdir'])

    tray.AddModule("MPHitFilter", "hitfilter",
                   HitOMThreshold=1,
                   RemoveBackgroundOnly=False,
                   I3MCPESeriesMapName=params['photonseriesname'])


    ### DETECTOR ###

    mcprescale = params['nproc']+1 if params['mcprescale']==0 else params['mcprescale']
    tray.AddSegment(segments.DetectorSegment, "detector",
                    gcdfile=params['gcdfile'],
                    mctype=params['mctype'],
                    uselineartree=params['uselineartree'],
                    detector_label=params['detectorname'],
                    runtrigger=params['trigger'],
                    filtertrigger=params['filtertrigger'],
                    stats=stats,
                    inice=not params['notinice'],
                    icetop=params['icetop'] or params['notinice'],
                    genie=params['genie'],
                    prescale=params['mcprescale'],
                    lowmem=params['lowmem'],
                    BeaconLaunches=params['beaconlaunches'],
                    TimeShiftSkipKeys=params['timeshiftskipkeys'],
                    SampleEfficiency=params['sampleefficiency'],
                    GeneratedEfficiency=params['generatedefficiency'],
                    RunID=params['runid'],
                    KeepMCHits=not params['procnum'] % mcprescale,#params['mcprescale'],
                    KeepPropagatedMCTree=not params['procnum'] % mcprescale,#params['mcprescale'],
                    KeepMCPulses=not params['procnum'] % mcprescale)#params['mcprescale'])


    if params['enablehistogram'] and params['histogramfilename']:
        tray.AddModule(ProductionHistogramModule,
                       Histograms=[I3MCTreePrimaryModule,
                                   I3MCTreeModule,
                                   I3MCPEModule,
                                   PMTResponseModule,
                                   InIceResponseModule,
                                   TriggerModule,
                                   NoiseOccupancy],
                       OutputFilename=params['histogramfilename'])
