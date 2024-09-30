oai_schema = {
  "title": "TeamState",
  "description": "A structured output representing the state of a team.",
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "description": "The assistant's message."
    },
    "sender": {
      "type": "string",
      "description": "The identifier of the sender."
    },
    "plan": {
      "type": "string",
      "description": "only for final security testing plan"
    }
  },
  "required": ["message", "sender", "plan"]
}
