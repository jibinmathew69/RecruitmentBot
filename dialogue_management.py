import rasa_core
from rasa_core.agent import Agent
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig
from rasa_core.run import serve_application


def train_dialogue(domain_file='domain.yml',
                   model_path='./models/dialogue',
                   training_data_file='./data/stories.md'):
    """
    This model trains the dialogue model and persist the model
    :param domain_file: Domain file
    :param model_path: Model persistence directory
    :param training_data_file: Story board file
    :return: Agent
    """
    fallback = FallbackPolicy(fallback_action_name="action_default_fallback",
                              core_threshold=0.3,
                              nlu_threshold=0.3)

    agent = Agent(domain_file, policies=[MemoizationPolicy(max_history=3), KerasPolicy(max_history=5, epochs=300, batch_size=50), fallback])
    data = agent.load_data(training_data_file)

    agent.train(data)

    agent.persist(model_path)
    return agent


def run_recruitment_bot():
    '''
    Initialize bot for chat.
    :return: agent
    '''
    interpreter = RasaNLUInterpreter('./models/nlu/default/current')
    action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
    agent = Agent.load('./models/dialogue', interpreter=interpreter, action_endpoint=action_endpoint)
    rasa_core.run.serve_application(agent, channel='cmdline')

    return agent


if __name__ == '__main__':
    train_dialogue()
    run_recruitment_bot()
