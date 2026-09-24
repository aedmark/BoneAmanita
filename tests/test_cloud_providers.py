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


def _ollama_send(llm, payload, reply=b'{"message":{"content":"hi"},"prompt_eval_count":12,"eval_count":3,"done_reason":"stop"}'):
    with patch('urllib.request.urlopen') as send:
        response = send.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = reply
        result = llm._transmit(payload)
    request = send.call_args.args[0]
    return result, request.full_url, json.loads(request.data)


def test_ollama_uses_the_native_endpoint_with_its_own_context():
    """/v1 cannot set num_ctx, so every model ran at Ollama's 4096 and long prompts were cut."""
    llm = LLMInterface(provider='ollama', model='gemma4:12b', base_url='http://127.0.0.1:11434/v1/chat/completions')
    result, url, sent = _ollama_send(llm, {'model': 'gemma4:12b', 'messages': [{'role': 'user', 'content': 'hello'}],
                                           'temperature': 0.8, 'top_p': 0.9, 'max_tokens': 500, 'stop': ['end'],
                                           'reasoning_effort': 'none', 'temperature_band': [0, 2]})
    assert url == 'http://127.0.0.1:11434/api/chat'
    assert result == 'hi'
    assert sent['think'] is False and sent['stream'] is False
    assert set(sent) == {'model', 'messages', 'stream', 'options', 'think'}
    opts = sent['options']
    assert opts['num_ctx'] == 32768
    assert (opts['temperature'], opts['top_p'], opts['num_predict'], opts['stop']) == (0.8, 0.9, 500, ['end'])
    assert llm.last_usage == {'prompt_tokens': 12, 'output_tokens': 3, 'done_reason': 'stop', 'num_ctx': 32768}


def test_ollama_reply_room_is_the_context_left_after_the_prompt():
    llm = LLMInterface(provider='ollama', model='m', base_url='http://host:11434/api/chat')
    long_prompt = 'x' * 90000
    _, url, sent = _ollama_send(llm, {'model': 'm', 'messages': [{'role': 'user', 'content': long_prompt}], 'max_tokens': 4096})
    assert url == 'http://host:11434/api/chat'
    assert sent['options']['num_predict'] == 32768 - 90000 // 3 - 64
