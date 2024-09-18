from workflows.pentest_team.launcher.worlflows_launcher import start_investigation_team_workflow




task = f"""
I have been provided with data from Nessus. Conduct an investigation of the host 63.251.228.70 according to this data only.

Nessus data:
    Vulnerabilities List:
    - Nessus UDP Scanner
    - Apache HTTP Server Version
    - Common Platform Enumeration (CPE)
    - HTTP Server Type and Version
    - HyperText Transfer Protocol (HTTP) Information
    - Nessus Scan Information
    - Non-compliant Strict Transport Security (STS)
    - Strict Transport Security (STS) Detection
    - Traceroute Information
    - Web Server No 404 Error Code Check
"""

start_investigation_team_workflow(task)