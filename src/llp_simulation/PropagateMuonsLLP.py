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
from .I3PropagatorServicePROPOSAL_LLP import I3PropagatorServicePROPOSAL_LLP
import math

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
                   entry_margin = 0,
                   exit_margin = 0,
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
    
    # check if good LLP event
    tray.Add(LLPEventCounter,
             nevents = nevents,
             only_save_LLP = OnlySaveLLPEvents,
             only_one_LLP  = kwargs["only_one_LLP"],
             GCDFile = gcdfile,
             both_prod_decay_inside = both_prod_decay_inside,
             min_LLP_length = min_LLP_length,
             entry_margin = entry_margin,
             exit_margin = exit_margin,
            )
    
    # Add empty MMCTrackList objects for events that have none.
    def add_empty_tracklist(frame):
        if "MMCTrackList" not in frame:
            frame["MMCTrackList"] = icecube.simclasses.I3MMCTrackList()
        return True
    
    tray.AddModule(add_empty_tracklist, name+"_add_empty_tracklist",
                Streams=[icecube.icetray.I3Frame.DAQ])
    
    # fix MMCTrackList "bug" that adds MMCTrack for LLP decay muons (PROPOSAL doesn't know if a muon is from LLP or not)
    def FixMMCTrackListLLP(frame, keyname="MMCTrackListLLP"):
        if keyname in frame:
            tracklist_LLP = frame[keyname]
            # highest energy muon is the initial muon from muongun
            initial_muon = max(tracklist_LLP, key = lambda track : track.Ei, default = None)
            if initial_muon is None:
                icecube.icetray.logging.log_error("no initial muon in " + str(keyname))
                frame["MMCTrackList"] = icecube.simclasses.I3MMCTrackList() # empty
                return False
            # create new MMCTrackList with only initial muon
            frame["MMCTrackList"] = icecube.simclasses.I3MMCTrackList([initial_muon])
            return True
        else:
            icecube.icetray.logging.log_error("no " + str(keyname) + " in frame!")
            return False
    # rename the "buggy" mmctracklist to a new key
    tray.AddModule("Rename", "rename MMCTrackList", Keys = ["MMCTrackList", "MMCTrackListLLP"])
    tray.Add(FixMMCTrackListLLP, streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics]) # no P frames in simulation but in case u dumb copy this code later

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
        
        self.only_one_LLP = True
        self.AddParameter("only_one_LLP", "Only save single LLP events", self.only_one_LLP)
        
        self.gcdFile = ""
        self.AddParameter("GCDFile", "GCD file which defines the in-ice volume", self.gcdFile)

        self.padding = 0. * icetray.I3Units.m # default no padding
        self.AddParameter("Padding", "", self.padding)
        
        # margins for LLP production and decay points
        self.entry_margin = 0. * icetray.I3Units.m
        self.AddParameter("entry_margin", "", self.entry_margin)
        
        self.exit_margin = 0. * icetray.I3Units.m
        self.AddParameter("exit_margin", "", self.exit_margin)
        
        self.min_LLP_length = 0.
        self.AddParameter("min_LLP_length", "minimum length for LLP to be good", self.min_LLP_length)
        
        self.both_prod_decay_inside = True
        self.AddParameter("both_prod_decay_inside", "Require LLP to have both production and decay point inside detector", self.both_prod_decay_inside)
        
    def Configure(self):
        self.only_save_LLP          = self.GetParameter("only_save_LLP")
        self.only_one_LLP          = self.GetParameter("only_one_LLP")
        self.nevents                = self.GetParameter("nevents")
        self.min_LLP_length         = self.GetParameter("min_LLP_length")
        self.gcdFile                = self.GetParameter("GCDFile") # create surface for detector volume
        self.padding                = self.GetParameter("Padding") # padding for gcd file
        self.entry_margin           = self.GetParameter("entry_margin") # how deep inside the detector the LLP production point must be
        self.exit_margin            = self.GetParameter("exit_margin") # how deep inside the detector the LLP decay point must be
        self.both_prod_decay_inside = self.GetParameter("both_prod_decay_inside")

        # use cylinder for detector volume if no gcd file
        if self.gcdFile != "":
            self.surface = MakeSurface(self.gcdFile, self.padding)
        else:
            self.surface = icecube.MuonGun.Cylinder(1000,500) # approximate detector volume
            
        self.tot_mu_propagated = 0
        self.llp_counter = {}
        self.xarr = []
        self.yarr = []
        self.zarr = []

    def DAQ(self, frame):
        """ only save frames that have one and only one good LLP event """
        self.tot_mu_propagated += 1
        if self.tot_mu_propagated%10000 == 0:
            icecube.icetray.logging.log_info("Tot mu/Tot saved events: ", self.tot_mu_propagated, self.event_count)
            # print("Fraction throughgoing LLP: ", self.llp_inside/self.tot_llp_count)
            icecube.icetray.logging.log_info("Count LLPs:", self.llp_counter)

        n_llp = frame["LLPInfo"]["interactions"]
        if n_llp in self.llp_counter:
            self.llp_counter[n_llp] += 1
        else:
            self.llp_counter[n_llp] = 1
        
        # Three options: save all, save all LLPs, save only single + good LLPs (should be standard)
        if self.only_save_LLP:
            if n_llp < 1:
                return False
            if self.only_one_LLP:
                if n_llp == 1 and self.CheckProductionDecayPoint(frame):
                    self.event_count += 1
                    self.xarr.append(frame["LLPInfo"]["prod_x"])
                    self.yarr.append(frame["LLPInfo"]["prod_y"])
                    self.zarr.append(frame["LLPInfo"]["prod_z"])
                else:
                    return False
            else:
                # checking good LLP makes no sense for N > 1
                self.event_count += 1
        else:
            self.event_count += 1
        
        if self.event_count == self.nevents:
            self.RequestSuspension()
            
        self.PushFrame(frame)
    
    def CheckProductionDecayPoint(self, frame):
        """ check that the LLP production and/or decay point is inside the geometry and that length is long enough """
        # no need to check vertices if gap length is too small        
        if frame["LLPInfo"]["length"] < self.min_LLP_length:
            return False
        
        direction  =              icecube.dataclasses.I3Direction(frame["LLPInfo"]["zenith"], frame["LLPInfo"]["azimuth"])
        production =              icecube.dataclasses.I3Position(frame["LLPInfo"]["prod_x"], frame["LLPInfo"]["prod_y"], frame["LLPInfo"]["prod_z"])
        decay      = production + icecube.dataclasses.I3Position(frame["LLPInfo"]["length"], direction.theta, direction.phi, icecube.dataclasses.I3Position.sph)
        
        prod_intersection  = self.surface.intersection(production, direction) # negative value means intersection behind point, positive means in front
        decay_intersection = self.surface.intersection(decay,      direction)
        
        # add margins to the production and decay points, reduces fiducial detector volume
        prod_intersection.first  += self.entry_margin
        prod_intersection.second -= self.exit_margin
        decay_intersection.first  += self.entry_margin
        decay_intersection.second -= self.exit_margin
        
        # production and decay vertex inside detector?
        prod_inside = (prod_intersection.first < 0 and prod_intersection.second > 0)
        decay_inside = (decay_intersection.first < 0 and decay_intersection.second > 0)

        good_LLP = False
        if self.both_prod_decay_inside:
            if prod_inside and decay_inside:
                good_LLP = True
        else:
            if prod_inside or decay_inside:
                good_LLP = True
            
        return good_LLP
        
    def Finish(self):
        icecube.icetray.logging.log_info(
            f"Finished simulation after {self.event_count} events.\n \
            Requested events: {self.nevents}\n \
            Total muons propagated: {self.tot_mu_propagated}\n \
            LLP counter: {self.llp_counter}"
        )
        # import matplotlib.pyplot as plt
        # plt.figure()
        # plt.hist(self.zarr, bins=100)
        # plt.show()
        
        # plotProductionPoints(self.xarr, self.yarr, self.zarr)
        return
    
# def plotProductionPoints(x,y,z):
#     import matplotlib.pyplot as plt
#     from mpl_toolkits.mplot3d import Axes3D
#     import numpy as np

#     # Create a 3D plot
#     fig = plt.figure(figsize=(12,12))  # Set the figure size to 10x8 inches
#     ax = fig.add_subplot(111, projection='3d')
#     ax.scatter(x, y, z)

#     # Plot a cylinder
#     height = 1000
#     radius = 500
#     resolution = 100
#     theta = np.linspace(0, 2 * np.pi, resolution)
#     z_cylinder = np.linspace(-height/2, height/2, resolution)
#     theta_grid, z_grid = np.meshgrid(theta, z_cylinder)
#     x_grid = radius * np.cos(theta_grid)
#     y_grid = radius * np.sin(theta_grid)
#     ax.plot_surface(x_grid, y_grid, z_grid, alpha=0.1, color='b')

#     # Set labels and title
#     ax.set_xlabel('X')
#     ax.set_ylabel('Y')
#     ax.set_zlabel('Z')
#     ax.set_title('Red = prod, Green = decay')

#     # Set all axes limits
#     xmin = -500
#     xmax = 500
#     ymin = -500
#     ymax = 500
#     zmin = -500
#     zmax = 500
    
#     ax.set_xlim([xmin, xmax])
#     ax.set_ylim([ymin, ymax])
#     ax.set_zlim([zmin, zmax])

#     # Show the plot
#     plt.show()
