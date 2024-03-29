@XTP-4912
Feature: SdpMasterLeafNode acceptance

	#Test the ability to generically run a a set of commands and that the execution is completed withing 5 seconds.
	@XTP-4908 @post_deployment @acceptance @SKA_mid @SKA_low
	Scenario: Ability to run commands on SdpMasterLeafNode
		Given a SdpMasterLeafNode device
		When I call the command <command_name>
		Then the command is queued and executed in less than 5 ss

		Examples:
		| command_name		   |
		| On                   |
        | Off                  |
		| Standby              |
        | Disable              |


	#Check SdpMasterLeafNode node correctly report failed and working devices defined within its scope of monitoring (internal model)
	@XTP-4909 @post_deployment @acceptance @SKA_mid @SKA_low
	Scenario Outline: Monitor SdpMasterLeafNode sub-devices
		Given a TANGO ecosystem with a set of devices deployed