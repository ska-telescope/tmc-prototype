@XTP-4913
Feature: SdpSubarrayLeafNode acceptance

	#Test the ability to generically run a a set of commands and that the execution is completed withing 5 seconds.
	@XTP-4910 @post_deployment @acceptance @SKA_mid @SKA_low
	Scenario: Ability to run commands on SdpSubarrayLeafNode
		Given a SdpSubarrayLeafNode device
		When I call the command <command_name>
		Then the command is queued and executed in less than 5 ss

		Examples:
		| command_name		   |
		| On                   |
		| Off				   |

	#Check SdpSubarrayLeafNode node correctly report failed and working devices defined within its scope of monitoring (internal model)
	@XTP-4911 @post_deployment @acceptance @SKA_mid @SKA_low
	Scenario Outline: Monitor SdpSubarrayLeafNode sub-devices
		Given a TANGO ecosystem with a set of devices deployed