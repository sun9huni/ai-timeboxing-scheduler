"""
음성 입력 기능 모듈
Chrome 브라우저의 Web Speech API를 사용하여 음성을 텍스트로 변환
"""
import streamlit as st
import streamlit.components.v1 as components

def render_voice_input_button(target_key: str, language: str = "ko-KR"):
    """
    음성 입력 버튼과 JavaScript 코드를 렌더링
    
    Args:
        target_key: 텍스트 입력 필드의 key
        language: 음성 인식 언어 (기본값: ko-KR)
    """
    
    # JavaScript 코드 - Chrome 최적화
    voice_input_js = f"""
    <script>
    let recognition_{target_key} = null;
    let isRecording_{target_key} = false;
    let finalTranscript_{target_key} = '';
    
    function initSpeechRecognition_{target_key}() {{
        // Chrome/Edge는 webkitSpeechRecognition 사용
        if ('webkitSpeechRecognition' in window) {{
            recognition_{target_key} = new webkitSpeechRecognition();
        }} else if ('SpeechRecognition' in window) {{
            recognition_{target_key} = new SpeechRecognition();
        }} else {{
            const statusEl = document.getElementById('voice-status-{target_key}');
            if (statusEl) {{
                statusEl.textContent = '❌ 브라우저 미지원';
                statusEl.style.color = '#ff4444';
            }}
            return;
        }}
        
        recognition_{target_key}.lang = '{language}';
        recognition_{target_key}.continuous = true;
        recognition_{target_key}.interimResults = true;
        recognition_{target_key}.maxAlternatives = 1;
        
        recognition_{target_key}.onstart = function() {{
            isRecording_{target_key} = true;
            finalTranscript_{target_key} = '';
            const statusEl = document.getElementById('voice-status-{target_key}');
            if (statusEl) {{
                statusEl.textContent = '🔴 듣는 중...';
                statusEl.style.color = '#ff4444';
            }}
            const btn = document.getElementById('voice-btn-{target_key}');
            if (btn) {{
                btn.style.background = 'linear-gradient(135deg, #ff4444 0%, #cc0000 100%)';
            }}
        }};
        
        recognition_{target_key}.onresult = function(event) {{
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {{
                    finalTranscript_{target_key} += transcript + '\\n';
                }} else {{
                    interimTranscript += transcript;
                }}
            }}
            
            const targetTextArea = findTextArea_{target_key}();
            
            if (targetTextArea) {{
                const currentText = targetTextArea.value || '';
                
                // 최종 결과가 있으면 추가
                if (finalTranscript_{target_key}) {{
                    // 기존 텍스트에 추가 (줄바꿈 처리)
                    let newText = currentText;
                    if (newText && !newText.endsWith('\\n') && !newText.endsWith(' ')) {{
                        newText += '\\n';
                    }}
                    newText += finalTranscript_{target_key};
                    targetTextArea.value = newText;
                    
                    // Streamlit에 변경 알림 (여러 이벤트 발생)
                    const inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
                    targetTextArea.dispatchEvent(inputEvent);
                    
                    const changeEvent = new Event('change', {{ bubbles: true, cancelable: true }});
                    targetTextArea.dispatchEvent(changeEvent);
                    
                    // Streamlit의 내부 이벤트도 발생
                    const keyupEvent = new KeyboardEvent('keyup', {{ bubbles: true, cancelable: true }});
                    targetTextArea.dispatchEvent(keyupEvent);
                    
                    // 값 변경 강제
                    Object.getOwnPropertyDescriptor(Object.getPrototypeOf(targetTextArea), 'value').set.call(targetTextArea, newText);
                    targetTextArea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    finalTranscript_{target_key} = '';
                }}
            }} else {{
                console.warn('Textarea not found for {target_key}');
            }}
        }};
        
        recognition_{target_key}.onerror = function(event) {{
            console.error('Speech recognition error:', event.error);
            const statusEl = document.getElementById('voice-status-{target_key}');
            if (statusEl) {{
                let errorMsg = '❌ 오류';
                if (event.error === 'no-speech') {{
                    errorMsg = '🔇 말씀해주세요';
                }} else if (event.error === 'audio-capture') {{
                    errorMsg = '🎤 마이크 확인';
                }} else if (event.error === 'not-allowed') {{
                    errorMsg = '🚫 권한 필요';
                }}
                statusEl.textContent = errorMsg;
                statusEl.style.color = '#ff4444';
            }}
            isRecording_{target_key} = false;
            resetButton_{target_key}();
        }};
        
        recognition_{target_key}.onend = function() {{
            isRecording_{target_key} = false;
            const statusEl = document.getElementById('voice-status-{target_key}');
            if (statusEl) {{
                statusEl.textContent = '🎤 음성 입력';
                statusEl.style.color = '#666';
            }}
            resetButton_{target_key}();
        }};
    }}
    
    function resetButton_{target_key}() {{
        const btn = document.getElementById('voice-btn-{target_key}');
        if (btn) {{
            btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }}
    }}
    
    function toggleVoiceRecording_{target_key}() {{
        if (!recognition_{target_key}) {{
            initSpeechRecognition_{target_key}();
            // 초기화 후 약간의 지연
            setTimeout(() => {{
                if (recognition_{target_key}) {{
                    try {{
                        recognition_{target_key}.start();
                    }} catch (e) {{
                        console.error('Failed to start recognition:', e);
                        const statusEl = document.getElementById('voice-status-{target_key}');
                        if (statusEl) {{
                            statusEl.textContent = '❌ 시작 실패';
                            statusEl.style.color = '#ff4444';
                        }}
                    }}
                }}
            }}, 100);
        }} else {{
            if (isRecording_{target_key}) {{
                try {{
                    recognition_{target_key}.stop();
                }} catch (e) {{
                    console.error('Failed to stop recognition:', e);
                }}
            }} else {{
                try {{
                    finalTranscript_{target_key} = '';
                    recognition_{target_key}.start();
                }} catch (e) {{
                    console.error('Failed to start recognition:', e);
                    const statusEl = document.getElementById('voice-status-{target_key}');
                    if (statusEl) {{
                        statusEl.textContent = '❌ 시작 실패';
                        statusEl.style.color = '#ff4444';
                    }}
                }}
            }}
        }}
    }}
    
    // 버튼 클릭 이벤트 연결
    function attachButtonEvent_{target_key}() {{
        const btn = document.getElementById('voice-btn-{target_key}');
        if (btn) {{
            // 기존 이벤트 리스너 제거 후 새로 추가
            btn.onclick = function(e) {{
                e.preventDefault();
                e.stopPropagation();
                toggleVoiceRecording_{target_key}();
                return false;
            }};
            return true;
        }}
        return false;
    }}
    
    // 전역 함수로 등록
    window.toggleVoiceRecording_{target_key} = toggleVoiceRecording_{target_key};
    window.attachButtonEvent_{target_key} = attachButtonEvent_{target_key};
    
    // 즉시 실행 및 주기적 체크
    (function init_{target_key}() {{
        // 음성 인식 초기화
        initSpeechRecognition_{target_key}();
        
        // 버튼 이벤트 연결 시도
        if (attachButtonEvent_{target_key}()) {{
            console.log('Voice button attached for {target_key}');
        }} else {{
            // 버튼이 아직 없으면 주기적으로 체크
            let attempts = 0;
            const checkInterval = setInterval(function() {{
                if (attachButtonEvent_{target_key}() || attempts++ > 10) {{
                    clearInterval(checkInterval);
                }}
            }}, 200);
        }}
    }})();
    </script>
    """
    
    # 버튼과 상태 표시 HTML
    button_html = f"""
    <div style="margin-top: 10px; text-align: center;">
        <button 
            id="voice-btn-{target_key}"
            onclick="window.toggleVoiceRecording_{target_key}()"
            style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 15px;
                font-weight: bold;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
                width: 100%;
                min-width: 120px;
            "
            onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 16px rgba(102, 126, 234, 0.4)';"
            onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.3)';"
            onmousedown="this.style.transform='scale(0.98)';"
            onmouseup="this.style.transform='scale(1.05)';"
        >
            <span id="voice-status-{target_key}" style="display: inline-block;">
                🎤 음성 입력
            </span>
        </button>
        <p style="font-size: 11px; color: #888; margin-top: 8px; line-height: 1.4;">
            Chrome 브라우저 권장<br/>
            마이크 권한 필요
        </p>
    </div>
    """
    
    # findTextArea 함수를 voice_input_js에 추가
    find_textarea_function = f"""
    // 부모 window에서 textarea 찾기 (iframe인 경우)
    function findTextArea_{target_key}() {{
        let targetTextArea = null;
        const searchWindow = window.parent !== window ? window.parent : window;
        
        // Streamlit의 textarea 찾기
        const textAreas = searchWindow.document.querySelectorAll('textarea');
        
        for (let textArea of textAreas) {{
            // Streamlit의 key 속성 확인
            const keyAttr = textArea.getAttribute('data-testid') || '';
            const nameAttr = textArea.getAttribute('name') || '';
            const idAttr = textArea.id || '';
            
            if (keyAttr.includes('{target_key}') || 
                nameAttr.includes('{target_key}') ||
                idAttr.includes('{target_key}')) {{
                targetTextArea = textArea;
                break;
            }}
        }}
        
        // 찾지 못하면 가장 가시적인 textarea 사용
        if (!targetTextArea && textAreas.length > 0) {{
            for (let textArea of textAreas) {{
                if (textArea.offsetHeight > 0 && textArea.offsetWidth > 0) {{
                    // 높이가 100 이상인 textarea (할 일 입력 영역일 가능성 높음)
                    if (textArea.offsetHeight > 100) {{
                        targetTextArea = textArea;
                        break;
                    }}
                }}
            }}
        }}
        
        return targetTextArea;
    }}
    """
    
    # voice_input_js에 findTextArea 함수 추가
    enhanced_js = voice_input_js.replace(
        'let finalTranscript_{target_key} = \'\';',
        f'let finalTranscript_{target_key} = \'\';\n    {find_textarea_function}'
    )
    
    # JavaScript와 버튼 HTML을 함께 렌더링
    combined_html = enhanced_js + button_html
    
    # Streamlit components로 렌더링
    components.html(combined_html, height=150)
