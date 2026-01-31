import speech_recognition as sr
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os

# ==========================================
# 【配置区】
# ==========================================
GEMINI_API_KEY = "AIzaSyD1-fnbfuKOluiFTOxHvWK8h2VXdsuePbc"
ELEVENLABS_API_KEY = "sk_f4b5b8896e27b6adae2639f527d327243f89e24e58f3c968"
VOICE_ID = "EST9Ui6982FZPSi7gCHi"

# --- 稳健的初始化方式 ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # 锁定 1.5-flash 模型，它是目前响应最快且最不容易报 404 的
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    print("✅ AI 客户端初始化成功！")
except Exception as e:
    print(f"❌ 客户端初始化失败: {e}")

# ==========================================
# 核心逻辑
# ==========================================

def simulate_hardware_action(action_name):
    """模拟发送给机器人的指令信号"""
    print(f"\n[硬件动作模拟] >>> ⚡ 机器人正在执行: {action_name}")

def chat_and_speak(text):
    """Gemini 思考 + ElevenLabs 说话"""
    print(f"\n[对话模式] 正在将 '{text}' 发送给 Gemini...")
    try:
        # 调用生成内容
        response = model.generate_content(
            f"You are a helpful robot. Give a short, witty response in the same language the user uses (under 20 words): {text}"
        )
        reply_text = response.text
        print(f"🤖 机器人回复: {reply_text}")

        # 调用 ElevenLabs
        print("🎙️ ElevenLabs 正在合成语音并播放...")
        audio = eleven_client.text_to_speech.convert(
            text=reply_text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2"
        )
        
        # 播放声音（确保电脑没静音）
        play(audio)
        
    except Exception as e:
        # 如果还是 404，这里会打印出详细原因
        print(f"⚠️ AI 交互出错: {e}")

def main_test_loop():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n" + "="*40)
    print("🚀 机器人大脑【本地测试版】已启动！")
    print("你可以说：'Forward'、'Left' 或者 随便聊两句")
    print("="*40)
    
    with mic as source:
        print("正在校准背景噪音...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("校准完成，请说话！")

    while True:
        try:
            with mic as source:
                print("\n🎤 监听中...")
                # 录音 5 秒，防止长时间卡住
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            # 设置为 en-US 以识别英语，它对中文的包容度也很高
            user_input = recognizer.recognize_google(audio, language="en-US").lower()
            print(f"👤 你说: {user_input}")

            # 动作匹配逻辑（支持中英文）
            if any(cmd in user_input for cmd in ["forward", "前进", "向前"]):
                simulate_hardware_action("FORWARD (前进)")
            elif any(cmd in user_input for cmd in ["backward", "后退"]):
                simulate_hardware_action("BACKWARD (后退)")
            elif any(cmd in user_input for cmd in ["left", "左转"]):
                simulate_hardware_action("TURN LEFT (左转)")
            elif any(cmd in user_input for cmd in ["right", "右转"]):
                simulate_hardware_action("TURN RIGHT (右转)")
            elif any(cmd in user_input for cmd in ["stop", "停"]):
                simulate_hardware_action("STOP (停止)")
            else:
                # 判定为闲聊模式
                chat_and_speak(user_input)

        except sr.UnknownValueError:
            print("❓ 没听清，请尝试大声一点...")
        except sr.WaitTimeoutError:
            continue
        except KeyboardInterrupt:
            print("\n👋 程序已关闭")
            break
        except Exception as e:
            print(f"🚨 发生意外错误: {e}")

if __name__ == "__main__":
    main_test_loop()