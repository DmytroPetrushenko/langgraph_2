# import functools
# import operator
#
# from langchain_core.messages import BaseMessage
#
# import forge
# from tools.msf_tools import msf_console_scan_tool_dynamic
# from workflows.pentest_team.graph_entities.statets import SubgraphState
# from workflows.pentest_team.graph_planning import PLANNING_TOOLS, PLANNING_NODE_NAME
# from workflows.pentest_team.graph_testing import TESTING_TOOLS, TESTING_NODE_NAME
# from workflows.pentest_team.launcher.worlflows_launcher import start_workflow_team
#
# # args = {
# #     'module_category': 'auxiliary',
# #     'module_name': 'scanner/http/files_dir',
# #     'path': '/',
# #     'rhosts': '63.251.228.70',
# #     'rport': 80,
# #     'threads': 1
# # }
# #
# # result = msf_console_scan_tool_dynamic(
# #     mock=False,
# #     **args
# # )
# #
# # print(result)
#
# # save_results_db(
# #     host="63.251.228.70",
# #     module="auxiliary/scanner/http/files_dir",
# #     output="[*] Using code '302' as not found for files with extension .backup, bak, c, cfg, class, copy, conf, exe, "
# #            "html, htm, ini, log, old, orig, php, tar, tar.gz",
# #     compressed_output="fuck"
# # )
# full_plan = """
# 1. Reconnaissance and Information Gathering:
#    - Use auxiliary/scanner/http/http_version to determine the web server version
#    - Employ auxiliary/scanner/http/robots_txt to check for any exposed directories
#    - Run auxiliary/scanner/http/dir_scanner to discover hidden directories
#    - Utilize auxiliary/scanner/http/http_header to analyze HTTP headers for potential vulnerabilities
#
# 2. Port Scanning and Service Enumeration:
#    - Execute auxiliary/scanner/portscan/tcp for a comprehensive TCP port scan
#    - Use auxiliary/scanner/portscan/syn for a stealthy SYN scan
#    - Run auxiliary/scanner/ssh/ssh_version to identify SSH version if port 22 is open
#    - Employ auxiliary/scanner/ftp/ftp_version for FTP version detection if port 21 is open
#
# 3. Web Application Analysis:
#    - Use auxiliary/scanner/http/dir_listing to check for directory listing vulnerabilities
#    - Run auxiliary/scanner/http/files_dir to search for sensitive files
#    - Employ auxiliary/scanner/http/http_login for potential web login pages
#    - Utilize auxiliary/scanner/http/backup_file to search for backup files
#
# 4. Vulnerability Assessment:
#    - Execute auxiliary/scanner/http/ssl_version to check for SSL/TLS vulnerabilities
#    - Run auxiliary/scanner/http/apache_optionsbleed if Apache server is detected
#    - Use auxiliary/scanner/http/cisco_ios_auth_bypass if Cisco devices are suspected
#    - Employ auxiliary/scanner/http/ms15_034_http_sys_memory_dump for Windows servers
#
# 5. Specific Exploit Attempts:
#    - If vulnerabilities are found, use appropriate exploit modules (not listed in auxiliary modules)
#
# 6. Post-Exploitation and Further Enumeration:
#    - If access is gained, use auxiliary/scanner/smb/smb_enumshares for SMB share enumeration
#    - Employ auxiliary/scanner/smb/smb_enumusers to list potential users
#    - Run auxiliary/scanner/mssql/mssql_login for MSSQL database access attempts
#
# 7. Data Exfiltration and Analysis:
#    - Use auxiliary/scanner/http/http_pdf_authors to gather potential user information from PDF metadata
#    - Employ auxiliary/scanner/http/files_dir to locate and download sensitive files
#    - Run auxiliary/analyze/crack_databases if any database hashes are obtained
#
# 8. Cleanup and Reporting:
#    - Document all findings, successful and unsuccessful attempts
#    - Remove any artifacts or payloads used during the pentest
#    - Compile a comprehensive report with vulnerabilities, risks, and recommendations
# """
from workflows.pentest_team.graph_testing import TESTING_TOOLS, TESTING_NODE_NAME

first_item_plan = """
1. Reconnaissance and Information Gathering:
   - Use auxiliary/scanner/http/http_version to determine the web server version
   - Employ auxiliary/scanner/http/robots_txt to check for any exposed directories
   - Run auxiliary/scanner/http/dir_scanner to discover hidden directories
   - Utilize auxiliary/scanner/http/http_header to analyze HTTP headers for potential vulnerabilities
"""

message_for_pentest_team = f"""
Now that we have the list of relevant modules, let's create a pentest plan for investigating the host 63.251.228.70 based on Metasploit modules:

Pentest Plan for Host 63.251.228.70

{first_item_plan}

Note: This plan should be executed with proper authorization and in compliance with all applicable laws and regulations. Always ensure you have explicit permission to test the target system.
"""
# # planning team
# import forge
# from workflows.pentest_team.graph_planning import PLANNING_TOOLS, PLANNING_NODE_NAME
# from workflows.pentest_team.launcher.worlflows_launcher import start_workflow_team
#
# message_for_planning_team = """
#     Create a pentest plan for investigating a host: 192.11.2.4!
# """
#
# model_llm = forge.create_llm('Claude 3.5 Sonnet')
#
# start_workflow_team(
#     input_message=message_for_planning_team,
#     model_llm=model_llm,
#     system_message_path='planning_team/operation_planner#1.txt',
#     tools=PLANNING_TOOLS,
#     team_name=PLANNING_NODE_NAME
# )
#
#
# pentest team
import forge
from workflows.pentest_team.launcher.worlflows_launcher import start_workflow_team

model_llm = forge.create_llm(model_name='gpt-4o')

start_workflow_team(
    input_message=message_for_pentest_team,
    model_llm=model_llm,
    system_message_path='testing_team/pentest_msf#1.txt',
    tools=TESTING_TOOLS,
    team_name=TESTING_NODE_NAME
)
# import forge
# from workflows.pentest_team.graph_entities.statets import SubgraphState
#
# # llm = forge.create_llm(model_name='gpt-4o')
# llm = forge.create_llm('Claude 3.5 Sonnet')
# structured_llm = llm.with_structured_output(SubgraphState)
#
# response = structured_llm.invoke("creat a security testing plan for investigating host 192.68.0.1")
#
# print(response)
