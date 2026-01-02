#!/usr/bin/env python3
# List all personas in the database

personas = env['ops.persona'].search([])
print(f"\nFound {len(personas)} personas:\n")
for persona in personas:
    print(f"  ID: {persona.id:3d} | Code: {persona.code:15s} | Name: {persona.name}")
