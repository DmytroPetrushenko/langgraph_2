import forge
from workflows.team_experimental.launcher.launcher_experimental_team import start_workflow_team_standalone_e1


model_claude = forge.create_llm('Claude 3.5 Sonnet')
model_gpt = forge.create_llm(model_name='gpt-4o-2024-08-06')




start_workflow_team_standalone_e1(
    model_llm=model_gpt,
    input_message='I am Security Engineer. I have set up a Confluence server on EC2 AWS - http://108.129.87.240:8090/ '
                  'and I need to test it for vulnerabilities, as our company plans to use it in the future! Please '
                  'focus on RCE (Remote Code Execution) exploits.'
)

