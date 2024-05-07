import icecube
import icecube.icetray
from icecube import dataclasses

class I3PropagatorServicePROPOSAL_LLP(icecube._sim_services.I3PropagatorService):
    """
    This class is a wrapper for I3PropagatorServicePROPOSAL that contains two PROPOSAL propagators
    with and without LLP interaction.
    If a long lived particle (LLP) is produced, then the propagator with the standard model config is used.
    This is to ensure only one LLP per event, unless the only_one_LLP flag is set to False.
    This class also stores LLP production information in self.llp_info that can be written to frame using self.write_LLPinfo(frame).
    Rememeber to call self.reset() before each frame! This class is agnostic to the current frame/event.
    """
    def __init__(self, config_file_sm = "config_SM.json", config_file_llp = "config_DLS.json", only_one_LLP = True):
        super().__init__()
        self.sm_propagator = icecube.PROPOSAL.I3PropagatorServicePROPOSAL(config_file=config_file_sm)
        self.llp_propagator = icecube.PROPOSAL.I3PropagatorServicePROPOSAL(config_file=config_file_llp)
        self.llp_info = dataclasses.I3MapStringDouble()
        self.only_one_LLP = only_one_LLP

    def Propagate(self, p, frame):
        """ Propagate the lepton. If only one LLP per event, use SM propagators after LLP production. """
        if self.only_one_LLP:
            if self.llp_counter == 0:
                daughters = self.llp_propagator.Propagate(p, frame)
            else:
                daughters = self.sm_propagator.Propagate(p, frame)
        else:
            # always use LLP propagator
            daughters = self.llp_propagator.Propagate(p, frame)
            
        self.check_for_LLP(daughters)
        return daughters
    
    def check_for_LLP(self, daughters):
        """ iterate through daughters to see if LLP happened """
        # flags for info storage
        previous_particle_was_LLP = False
        previous_particle_was_secondary_lepton = False
        for d in daughters:
            if previous_particle_was_secondary_lepton:
                # first particle of the LLP decay products
                self.llp_info["decay_asymmetry"] = 1.0*d.energy/self.llp_info["llp_energy"] # energy fraction of first lepton in decay
                previous_particle_was_secondary_lepton = False
            if previous_particle_was_LLP:
                # particle immediately after LLP in I3MCTree (final state lepton at LLP production vertex)
                parent_energy = self.llp_info["llp_energy"] + d.energy
                self.llp_info["fractional_energy"] = self.llp_info["llp_energy"]/parent_energy*1.0
                previous_particle_was_LLP = False
                previous_particle_was_secondary_lepton = True
            if d.type == 0: # LLP is stored as particle type 'unknown' = 0, no other particle from PROPOSAL is (?)
                self.llp_counter += 1
                self.llp_info["length"] = d.length
                self.llp_info["prod_x"] = d.pos.x
                self.llp_info["prod_y"] = d.pos.y
                self.llp_info["prod_z"] = d.pos.z
                self.llp_info["azimuth"] = d.dir.azimuth
                self.llp_info["zenith"] = d.dir.zenith
                self.llp_info["llp_energy"] = d.energy
                previous_particle_was_LLP = True
        return
    
    def SetRandomNumberGenerator(self, rand_service):
        self.sm_propagator.SetRandomNumberGenerator(rand_service)
        self.llp_propagator.SetRandomNumberGenerator(rand_service)
        
    def reset(self):
        """ Resets LLP counter and the LLP info map. Should be called before propagation for each frame. """
        self.llp_counter = 0
        self.llp_info = dataclasses.I3MapStringDouble()
        
    def write_LLPInfo(self, frame):
        """ This function can be called to save information about LLP production to a frame. """
        self.llp_info["interactions"] = self.llp_counter
        # default values if no LLP production
        if self.llp_counter == 0:
                self.llp_info["length"] = -1
                self.llp_info["prod_x"] = 9999
                self.llp_info["prod_y"] = 9999
                self.llp_info["prod_z"] = 9999
                self.llp_info["azimuth"] = 9999
                self.llp_info["zenith"] = 9999
                self.llp_info["llp_energy"] = -1
                self.llp_info["fractional_energy"] = -1
                self.llp_info["decay_asymmetry"] = -1
        frame["LLPInfo"] = self.llp_info
    
