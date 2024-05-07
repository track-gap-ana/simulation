"""
Tray segments for muon propagation with Long Lived Particle (LLP) interaction. This is a modification of simprod-scripts PropagateMuons.py
"""
import os

import icecube
import icecube.icetray as icetray
import icecube.dataclasses
import icecube.phys_services
import icecube.sim_services
import icecube.simclasses
import icecube.cmc
import icecube.PROPOSAL
import icecube.MuonGun
import icecube.dataio
import json
import numpy as np
from I3PropagatorServicePROPOSAL_LLP import I3PropagatorServicePROPOSAL_LLP

@icecube.icetray.traysegment
def PropagateMuonsLLP(tray, name,
                   RandomService=None,
                   CylinderRadius=None,
                   CylinderLength=None,
                   SaveState=True,
                   InputMCTreeName="I3MCTree_preMuonProp",
                   OutputMCTreeName="I3MCTree",
                   PROPOSAL_config_SM="config_SM.json",
                   PROPOSAL_config_LLP="config_DLS.json",
                   OnlySaveLLPEvents=True,
                   nevents = 1,
                   gcdfile = "",
                   both_prod_decay_inside = True,
                   min_LLP_length = 0,
                   **kwargs):
    r"""Propagate muons.

    This segment propagates muons through ice with ``PROPOSAL``; it
    simulates lepton decays and energy losses due to ionization,
    bremsstrahlung, photonuclear interactions, and pair production.
    It also includes Long Lived Particle (LLP) production.

    :param I3RandomService RandomService:
        Random number generator service
    :param float CylinderRadius:
        Radius of the target volume in m
        (this param is now depricated, use the config file in the detector configuration)
    :param float CylinderLength:
        Full height of the target volume in m
        (this param is now depricated, use the config file in the detector configuration)
    :param bool SaveState:
        If set to `True`, store the state of the supplied RNG.
    :param str InputMCTree:
        Name of input :ref:`I3MCTree` frame object
    :param str OutputMCTree:
        Name of output :ref:`I3MCTree` frame object
    :param \**kwargs:
        Additional keyword arguments are passed to
        :func:`icecube.simprod.segments.make_propagator`.

    """
    if CylinderRadius is not None:
        icecube.icetray.logging.log_warn(
            "The CylinderRadius now should be set in the configuration file in the detector configuration")
    if CylinderLength is not None:
        icecube.icetray.logging.log_warn(
            "The CylinderLength now should be set in the configuration file in the detector configuration")
    propagator_map, muon_propagator = make_propagators(tray, PROPOSAL_config_SM, PROPOSAL_config_LLP, **kwargs)

    if SaveState:
        rng_state = InputMCTreeName+"_RNGState"
    else:
        rng_state = ""

    # write simulation information to S frame
    tray.Add(write_simulation_information,
             PROPOSAL_config_LLP = PROPOSAL_config_LLP,
             Streams=[icecube.icetray.I3Frame.Simulation])
    
    # reset the LLP info before each event
    tray.Add(lambda frame : muon_propagator.reset(), 
             Streams=[icecube.icetray.I3Frame.DAQ])

    tray.AddModule("I3PropagatorModule", name+"_propagator",
                   PropagatorServices=propagator_map,
                   RandomService=RandomService,
                   InputMCTreeName=InputMCTreeName,
                   OutputMCTreeName=OutputMCTreeName,
                   RNGStateName=rng_state)

    # write LLP information to frame
    tray.Add(lambda frame : muon_propagator.write_LLPInfo(frame), 
             Streams=[icecube.icetray.I3Frame.DAQ])
    
    # Add empty MMCTrackList objects for events that have none.
    def add_empty_tracklist(frame):
        if "MMCTrackList" not in frame:
            frame["MMCTrackList"] = icecube.simclasses.I3MMCTrackList()
        return True

    tray.AddModule(add_empty_tracklist, name+"_add_empty_tracklist",
                   Streams=[icecube.icetray.I3Frame.DAQ])
    
    tray.Add(LLPEventCounter,
             nevents = nevents,
             only_save_LLP = OnlySaveLLPEvents,
             GCDFile = gcdfile,
             both_prod_decay_inside = both_prod_decay_inside,
             min_LLP_length = min_LLP_length,
            )
    
    return

def make_propagators(tray,                     
                     PROPOSAL_config_SM,
                     PROPOSAL_config_LLP,
                     only_one_LLP = True,
                     SplitSubPeVCascades=True,
                     EmitTrackSegments=True,
                     MaxMuons=10,
                     ):
    """
    Set up propagators (PROPOSAL for muons and taus with LLP interaction, CMC for cascades)

    :param bool SplitSubPeVCascades: Split cascades into segments above 1 TeV. Otherwise, split only above 1 PeV.
    
    """
    from icecube.icetray import I3Units

    cascade_propagator = icecube.cmc.I3CascadeMCService(
        icecube.phys_services.I3GSLRandomService(1))  # Dummy RNG
    cascade_propagator.SetEnergyThresholdSimulation(1*I3Units.PeV)
    if SplitSubPeVCascades:
        cascade_propagator.SetThresholdSplit(1*I3Units.TeV)
    else:
        cascade_propagator.SetThresholdSplit(1*I3Units.PeV)
    cascade_propagator.SetMaxMuons(MaxMuons)
    
    muon_propagator = I3PropagatorServicePROPOSAL_LLP(PROPOSAL_config_SM, PROPOSAL_config_LLP, only_one_LLP)
    propagator_map = icecube.sim_services.I3ParticleTypePropagatorServiceMap()

    for pt in "MuMinus", "MuPlus", "TauMinus", "TauPlus":
        key = getattr(icecube.dataclasses.I3Particle.ParticleType, pt)
        propagator_map[key] = muon_propagator

    for key in icecube.sim_services.ShowerParameters.supported_types:
        propagator_map[key] = cascade_propagator
    
    return propagator_map, muon_propagator

def write_simulation_information(frame, PROPOSAL_config_LLP):
    """ Write LLP multiplier, mass, epsilon, etc. to S frame """
    if "LLPConfig" not in frame:
        file = open(PROPOSAL_config_LLP)
        config_json = json.load(file)
        
        simulation_info = icecube.dataclasses.I3MapStringDouble()
        simulation_info["llp_multiplier"] = config_json["global"]["llp_multiplier"]
        simulation_info["mass"] = config_json["global"]["llp_mass"]
        simulation_info["epsilon"] = config_json["global"]["llp_epsilon"]
        simulation_model = icecube.dataclasses.I3String(config_json["global"]["llp"])

        frame["LLPConfig"] = simulation_info
        frame["LLPModel"] = simulation_model
        
        file.close()
        

#Function to read the GCD file and make the extruded polygon which
#defines the edge of the in-ice array
def MakeSurface(gcdName, padding):
    file = icecube.dataio.I3File(gcdName, "r")
    frame = file.pop_frame()
    while not "I3Geometry" in frame:
        frame = file.pop_frame()
    geometry = frame["I3Geometry"]
    xyList = []
    zmax = -1e100
    zmin = 1e100
    step = int(len(geometry.omgeo.keys())/10)
    print("Loading the DOM locations from the GCD file")
    for i, key in enumerate(geometry.omgeo.keys()):
        if i % step == 0:
            print( "{0}/{1} = {2}%".format(i,len(geometry.omgeo.keys()), int(round(i/len(geometry.omgeo.keys())*100))))
            
        if key.om in [61, 62, 63, 64] and key.string <= 81: #Remove IT...
            continue

        pos = geometry.omgeo[key].position

        if pos.z > 1500:
            continue
            
        xyList.append(pos)
        i+=1
    
    return icecube.MuonGun.ExtrudedPolygon(xyList, padding) 
        
class LLPEventCounter(icetray.I3Module):
    """ class that counts how many events before finishing simulation """
    def __init__(self, ctx):
        icetray.I3Module.__init__(self, ctx)
        self.event_count = 0
        self.nevents = 0
        self.AddParameter("nevents", "Number of events to simulate", self.nevents)

        self.only_save_LLP = True
        self.AddParameter("only_save_LLP", "Only save LLP events", self.only_save_LLP)
        
        self.gcdFile = ""
        self.AddParameter("GCDFile", "GCD file which defines the in-ice volume", self.gcdFile)

        self.padding = 60. * icetray.I3Units.m # default 60 m padding
        self.AddParameter("Padding", "", self.padding)
        
        self.min_LLP_length = 0.
        self.AddParameter("min_LLP_length", "minimum length for LLP to be good", self.min_LLP_length)
        
        self.both_prod_decay_inside = True
        self.AddParameter("both_prod_decay_inside", "Require LLP to have both production and decay point inside detector", self.both_prod_decay_inside)
        
    def Configure(self):
        self.only_save_LLP          = self.GetParameter("only_save_LLP")
        self.nevents                = self.GetParameter("nevents")
        self.min_LLP_length         = self.GetParameter("min_LLP_length")
        self.gcdFile                = self.GetParameter("GCDFile") # create surface for detector volume
        self.padding                = self.GetParameter("Padding") # padding for gcd file
        self.both_prod_decay_inside = self.GetParameter("both_prod_decay_inside")

        # use cylinder for detector volume if no gcd file
        if self.gcdFile != "":
            self.surface = MakeSurface(self.gcdFile, self.padding)
        else:
            self.surface = icecube.MuonGun.Cylinder(1000,500) # approximate detector volume

    def DAQ(self, frame):
        """ only save frames that have one and only one good LLP event """
        if self.only_save_LLP:
            if frame["LLPInfo"]["interactions"] == 1 and self.CheckProductionDecayPoint(frame):
                self.event_count += 1
            else:
                return False
        else:
            self.event_count += 1
        
        if self.event_count == self.nevents:
            self.RequestSuspension()
            
        self.PushFrame(frame)
        
    def CheckProductionDecayPoint(self, frame):
        """ check that the LLP production and/or decay point is inside the geometry and that length is long enough """
        if frame["LLPInfo"]["length"] < self.min_LLP_length:
            return False
        
        direction  =              icecube.dataclasses.I3Direction(frame["LLPInfo"]["zenith"], frame["LLPInfo"]["azimuth"])
        production =              icecube.dataclasses.I3Position(frame["LLPInfo"]["prod_x"], frame["LLPInfo"]["prod_y"], frame["LLPInfo"]["prod_z"])
        decay      = production + icecube.dataclasses.I3Position(frame["LLPInfo"]["length"], direction.theta, direction.phi, icecube.dataclasses.I3Position.sph)
        
        prod_intersection  = self.surface.intersection(production, direction) # negative value means intersection behind point, positive means in front
        decay_intersection = self.surface.intersection(decay,      direction)
        
        good_LLP = False
        if self.both_prod_decay_inside:
            if prod_intersection.first*prod_intersection.second < 0 and decay_intersection.first*decay_intersection.second < 0:
                good_LLP = True
        else:
            if prod_intersection.first*prod_intersection.second < 0 or decay_intersection.first*decay_intersection.second < 0:
                good_LLP = True
            
        return good_LLP
            
        
            
        