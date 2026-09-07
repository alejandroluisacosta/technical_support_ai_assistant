# Decisions

## No assumed facts in the analysis output

The exercise asks the solution to distinguish confirmed information from assumptions and not invent technical details.

This solution goes further: it does not emit assumptions at all. Factual fields used for troubleshooting and escalation (`environment`, `application`, `error_messages`, `object_ids`) are either `confirmed` (quoted from the ticket) or `unknown`. There is no `assumptions` field.

Assumed technical details are more harmful than useful in this workflow. Support already treats model output with caution because models often draw on outdated documentation or invent specifics. Filling gaps with guessed error codes or root causes creates noise in Support tickets and lowers trust in the ticket review tool.

Unknown slots are the useful signal: they drive `missing_information` questions to the customer instead of fabricating a complete picture.

Classification and priority remain judgments. Those calls may be made from confirmed facts and known gaps. They must not be justified with invented technical details.

## No invented troubleshooting or escalation

The exercise asks for recommended troubleshooting steps and an escalation recommendation.

This solution does not generate either yet. `troubleshooting_steps` and `escalation_reason` are fixed placeholders. `escalate_to_development` is always `false`.

The tool has no access to product documentation. Generic model advice would be guessed or drawn from outdated material, which Support already distrusts. Those fields will be filled only after the tool can ground them in current solution docs.

## With more time, I would

- Reduce the questions made by the agent to the end user. Currently, it returns 5-6 questions and some of them would be irritating to users.
- Improve the quality of the proposed customer-facing response, as it is currently a repetition of the issue plus the questions it wants to make.
- Find a way to provide reliable troubleshooting steps and escalation reason. I explicitly decided to maintain these as placeholders for the time being, but if connected to the company's documentation, these would potentially be the most useful data points returned to the Support Engineer to further process the ticket.
