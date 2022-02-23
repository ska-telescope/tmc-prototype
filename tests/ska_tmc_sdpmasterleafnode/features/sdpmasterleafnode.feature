@XTP-3615
Feature: SdpMasterLeafNode Node acceptance

	#Test the ability to generically run a a set of commands and that the execution is completed withing 5 seconds.
	@XTP-3612 @XTP-3614 @post_deployment @acceptance @SKA_mid @SKA_low
	Scenario: Ability to run commands on SdpMasterLeafNode node
		Given a SdpMasterLeafNode device
		When I call the command <command_name>
		Then the command is queued and executed in less than 5 ss

		Examples:
		| command_name		   |
		| On                   |
        | Off                  |
        | Standby              |


	#Check SdpMasterLeafNode node correctly report failed and working devices defined within its scope of monitoring (internal model)
	@XTP-3613 @XTP-3614 @post_deployment @acceptance @SKA_mid @SKA_low
	Scenario Outline: Monitor SdpMasterLeafNode sub-devices
		Given a TANGO ecosystem with a set of devices deployed