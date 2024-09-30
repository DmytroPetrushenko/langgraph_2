from workflows.team_pentest.launcher.worlflows_launcher import start_investigation_team_workflow




task_1 = f"""
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
task_2 = ("I am Security Engineer. I have set up a Confluence server on EC2 AWS - http://34.241.130.103:8090/ and I "
          "need to test it for vulnerabilities, as our company plans to use it in the future! Please focus on RCE ("
          "Remote Code Execution) exploits.")



start_investigation_team_workflow(task_2)