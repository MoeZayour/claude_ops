Restart the Odoo Docker container and verify startup.

## Instructions

1. Restart the container:
```bash
docker restart gemini_odoo19
```

2. Wait for startup then verify:
```bash
sleep 5 && docker ps --filter name=gemini_odoo19 --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

3. Check for startup errors:
```bash
docker logs gemini_odoo19 --tail 20 2>&1 | grep -E "(ERROR|error|running on|Odoo server)"
```

4. Quick health check:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8089/web/login
```
Expected: 200

5. Report:
   - Container status (running/stopped)
   - Port bindings (should be 8089)
   - Any errors found
   - HTTP response code
