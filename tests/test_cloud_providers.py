import json
from unittest.mock import patch
import pytest
from brain.composer import LLMInterface, TransientError
from mechanics.providers import environment_config


def test_environment_switch_does_not_reuse_local_endpoint():
    with patch.dict('os.environ', {'BONE_PROVIDER': 'grok', 'BONE_MODEL': 'chosen', 'XAI_API_KEY': 'secret'}):
        cfg = environment_config({'provider': 'ollama', 'base_url': 'http://localhost', 'model': 'local'})
    assert cfg['provider'] == 'xai'
    assert cfg['base_url'] == 'https://api.x.ai/v1/chat/completions'
    assert cfg['model'] == 'chosen'


@pytest.mark.parametrize('provider', ['xai', 'anthropic'])
def test_cloud_ignores_ollama_url(provider):
    with patch.dict('os.environ', {'OLLAMA_BASE_URL': 'http://local'}):
        llm = LLMInterface(provider=provider, api_key='test', model='chosen')
    assert llm.base_url.startswith('https://api.')


def test_anthropic_wire_format_and_response():
    llm = LLMInterface(provider='claude', api_key='test', model='chosen')
    with patch('urllib.request.urlopen') as send:
        response = send.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b'{"content":[{"type":"thinking","thinking":"hidden"},{"type":"text","text":"hello"}]}'
        result = llm._transmit({'model':'chosen', 'messages':[], 'temperature':1.8, 'top_p':.9, 'stop':['end'], 'temperature_band':[0,2]})
    request = send.call_args.args[0]
    payload = json.loads(request.data)
    assert payload['temperature'] == 1
    assert payload['max_tokens'] == 1024
    assert payload['stop_sequences'] == ['end']
    assert 'top_p' not in payload and 'temperature_band' not in payload
    assert request.get_header('X-api-key') == 'test'
    assert request.get_header('Authorization') is None
    assert result == 'hello'


def test_strict_live_never_falls_back():
    with patch.dict('os.environ', {'BONE_STRICT_LIVE':'1'}):
        llm = LLMInterface(provider='xai', api_key='test', model='chosen')
    with patch.object(llm, '_transmit', side_effect=TransientError('offline')), patch.object(llm, '_local_fallback') as fallback:
        with pytest.raises(TransientError):
            llm.generate('hello', {})
    fallback.assert_not_called()
    assert llm.live_failures == 1
