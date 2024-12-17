from os.path import expanduser
from datetime import date, datetime
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from llama_cpp import Llama
import json
import bot_template
                
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                
                
template = bot_template.chat_template


def load_model(model_path, callback_manager):
      llm = Llama(
        model_path=model_path,
        n_gpu_layers=-1,
        n_batch=4096,
        callback_manager=callback_manager,
        verbose=True,  # Verbose is required to pass to the callback manager
        streaming=True,
        n_ctx=30000,
        last_n_tokens_size = 256,
        top_k = 1,
        echo = False,
        stop = [
      "<|end_of_text|>",
      "(note)",
      "( note )",
      "Time :",
      "<|im_end|>"
    ],
    )
      return llm

def infer(chat, llm, history, user_input, debug=False, tries=10):
      result = False
      i = 0
      emotions = ["excited", "happy", "sad", "serious", "informative", "confused", "neutral", "angry", "surprised", "worried", "wonder", "light joy", "annoyed", "disappointed", "curious", "proud"]
      while i < tries:
            print(f"loop {i}")
            i += 1
            model_output = llm(
            chat,
            max_tokens=None,
            stop = ["<|end_of_text|>","(note)","( note )", "<|im_end|>"],
            echo=False
            )
            output = model_output["choices"][0]["text"]
            
            try:  
                  check_threshold = 0
                  if "respond" not in output:
                        print("no respond")
                        print(output)
                  formatter = bot_template.formatter.format(output=output)
                  formatted_output = llm(
                        formatter,
                        max_tokens=None,
                        stop = ["<|end_of_text|>","(note)","( note )", "<|im_end|>"],
                        echo=False
                        )
                  formatted_output = formatted_output["choices"][0]["text"]
                  result = json.loads(formatted_output)
                  if result["emotion"] not in emotions:
                        print("emotion not found.")
                  checker = bot_template.checker.format(user_input=user_input, thought=result["thought"], respond=result["respond"])
                  while check_threshold < 10:
                        check_threshold += 1
                        check = llm(
                                    checker,
                                    max_tokens=None,
                                    stop = ["<|end_of_text|>","(note)","( note )", "<|im_end|>"],
                                    echo=False
                                    )
                        check = check["choices"][0]["text"]
                        json_checker = bot_template.json_checker.format(text=check)
                        formatted_check = llm(
                                                json_checker,
                                                max_tokens=None,
                                                stop = ["<|end_of_text|>","(note)","( note )", "<|im_end|>"],
                                                echo=False
                                                )
                        
                        formatted_check = formatted_check["choices"][0]["text"]
                        try:
                              check_result = json.loads(formatted_check)
                              if check_result["answer"]:
                                    break
                        except Exception as e:
                              print(f"error {e}")
                              print(check)
                              print("Error converting json")
                              continue
                  
            except Exception as e:
                  print(e)
                  print(output)
                  continue
            
            if result and check_result["answer"] == "yes":
                  print("approved, " + check_result["reason"])
                  break
            
            elif check_result["answer"] == "no":
                  print("rejected, " + check_result["reason"])
                  print(result)
                  continue
            
            if i >= tries:
                  print(f"failed to generate respond after {i} tries.")
                  return output, history
      
      summarize_prompt = bot_template.summarize_prompt.format(user_input=user_input, history=history, result=result)    
      summarize = llm(     summarize_prompt,
                        max_tokens=None,
                        stop = ["<|end_of_text|>","(note)","( note )", "<|im_end|>"],
                        echo=False
                        )
      summarize = summarize["choices"][0]["text"]            
      
      if debug:
            return output, summarize
      else: 
            return result, summarize

if __name__ == "__main__":
      
      model_path = expanduser(r"/home/unstaple/LLama/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf")
      callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
      llm = load_model(model_path, callback_manager)
      history = f"I just got boosted up on discord server at {days[date.today().weekday()]} {(str(datetime.now()))[:-7]}"
      
      def test(text):
            global history
            text += ', "time" : "{weekday} {day}"'.format(weekday=days[date.today().weekday()], day=(str(datetime.now()))[:-7]) + "}"
            chat = template.format(chat_history=history, text=text)
            result, history = infer(chat, llm, history, text)
            
            print(result)
            print(history)
            print(f'respond : {result["respond"]}\nemotion : {result["emotion"]}')
      

      test(text='{"name" : "stapler_x", "message" : "Hi, Don. Do you familia with me?')
      test(text='{"name" : "stapler_x", "message" : "Can you tell me the time?')
      test(text='{"name" : "stapler_x", "message" : "Do you remember what did I tell you when you was just boosted up?')