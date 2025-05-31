# @title **Trợ lý Lập trình Thông minh (Smart Programming Assistant) - Phiên bản 1.0**

# Cài đặt thư viện cần thiết
# Make sure to install google-generativeai: pip install google-generativeai
# Make sure to install Flask: pip install Flask
# Make sure to install python-dotenv: pip install python-dotenv

import os
import re
import textwrap
import google.generativeai as genai  # Use Google's Gemini API
import json
from flask import Flask, render_template, request
from markupsafe import Markup
from dotenv import load_dotenv # Added for loading .env file

# CÀI ĐẶT ENV

# CHỈ load .env khi file .env còn tồn tại (dành cho local dev)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)



app = Flask(__name__)

# Global variables
model_name_global = None
gemini_model_global = None  # Global Gemini model

# Cấu hình API key cho Gemini
def setup_gemini_api():
  load_dotenv()  # Load environment variables from .env file
  global model_name_global, gemini_model_global
  try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Chưa thiết lập GEMINI_API_KEY trong .env")
        #sys.exit(1)

    genai.configure(api_key=api_key)
    
    model_to_use = "gemini-2.5-flash-preview-05-20"  # or "gemini-pro" if you prefer
    
    # Test the connection by initializing a model
    try:
        # Initialize the model
        gemini_model_global = genai.GenerativeModel(model_to_use)
        
        # Simple test to see if the model can be accessed
        test_response = gemini_model_global.generate_content("Hello")
        if test_response:
            print(f"✅ Google Gemini API key configured and authenticated! Using model: {model_to_use}")
        else:
            raise Exception("Model returned empty response")
            
    except Exception as auth_err:
        print(f"❌ Lỗi xác thực Gemini API: {str(auth_err)}")
        print("Vui lòng kiểm tra lại API key.")
        model_name_global = None
        gemini_model_global = None
        return False
        
    model_name_global = model_to_use
    return True
  except Exception as e:
    print(f"❌ Lỗi khi cấu hình Gemini API: {str(e)}")
    model_name_global = None
    gemini_model_global = None
    return False

# Cải thiện create_prompt cho phần mô phỏng thực thi rõ ràng hơn
def create_prompt(problem_description, source_code, language):
  # Define the JSON example structure as a separate string
  json_example_structure = """\
{
    "overview": {
      "summary": "Tóm tắt chức năng của mã nguồn...",
      "meets_requirements": true/false/partial,
      "explanation": "Giải thích mức độ đáp ứng yêu cầu đề bài..."
    },
    "complexity_analysis": {
      "time_complexity": "O(n), O(n²), O(log n), etc.",
      "space_complexity": "O(n), O(1), etc.",
      "explanation": "Giải thích chi tiết về độ phức tạp và hiệu suất..."
    },
    "errors": {
      "syntax_errors": [
        {
          "line": "số_dòng",
          "severity": "high/medium/low",
          "description": "Mô tả lỗi cú pháp...",
          "impact": "Tác động của lỗi đến chương trình..."
        }
      ],
      "logical_errors": [
        {
          "line": "số_dòng",
          "severity": "high/medium/low",
          "description": "Mô tả lỗi logic...",
          "impact": "Tác động của lỗi đến chương trình..."
        }
      ],
      "potential_issues": [
        {
          "line": "số_dòng",
          "severity": "high/medium/low",
          "description": "Mô tả vấn đề tiềm ẩn...",
          "scenario": "Kịch bản khi vấn đề có thể xảy ra..."
        }
      ]
    },
    "fix_suggestions": [
      {
        "line": "số_dòng",
        "error_type": "syntax/logical/potential",
        "priority": "required/optional",
        "original_code": "Đoạn mã gốc có lỗi...",
        "fixed_code": "Đoạn mã đã sửa...",
        "explanation": "Giải thích chi tiết cách sửa và lý do..."
      }
    ],
    "simulation": {
      "error_case": {
        "input": "Giá trị đầu vào gây lỗi hoặc 'Không tìm thấy trường hợp lỗi rõ ràng'",
        "steps": [
          {
            "step": 1,
            "line": "số_dòng",
            "code_line": "Dòng code GỐC đang thực thi...",
            "explanation": "Giải thích bước...",
            "variables": {
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            },
            "is_error_step": false,
            "error_explanation": null
          }
        ],
        "result": "Kết quả sai/lỗi thu được từ mã gốc (nếu có)"
      },
      "success_case": {
        "input": "Giá trị đầu vào chạy đúng hoặc 'Không tìm thấy trường hợp chạy thành công'",
        "steps": [
          {
            "step": 1,
            "line": "số_dòng",
            "code_line": "Dòng code GỐC đang thực thi...",
            "explanation": "Giải thích bước...",
            "variables": {
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            }
          }
        ],
        "result": "Kết quả đúng thu được từ mã gốc (nếu có)"
      }
    },
    "advanced_improvements": [
      {
        "type": "optimization/design/algorithm/data_structure",
        "description": "Mô tả cải tiến nâng cao...",
        "benefit": "Lợi ích của cải tiến này...",
        "code_example": "Ví dụ minh họa ngắn gọn cho cải tiến (nếu có)..."
      }
    ],
    "learning_guidance": {
      "evaluation": "Đánh giá tổng quát về mã nguồn, điểm mạnh và điểm yếu...",
      "concepts_to_learn": ["Khái niệm 1", "Khái niệm 2", "..."],
      "resources": [
        {
          "topic": "Chủ đề học tập liên quan...",
          "why_relevant": "Lý do tại sao chủ đề này quan trọng với người dùng...",
          "difficulty": "beginner/intermediate/advanced"
        }
      ]
    }
  }"""

  prompt = f"""
  Bạn là một trợ lý lập trình thông minh chuyên phân tích và debug mã nguồn {language}, với kinh nghiệm đặc biệt trong việc giải quyết các thuật toán và tối ưu hóa code. Nhiệm vụ của bạn là giúp phân tích, tìm lỗi và đề xuất cải tiến cho đoạn code sau:
  
  # Đề bài:
  {problem_description}
  
  # Mã nguồn {language} (DO NGƯỜI DÙNG CUNG CẤP):
  ```{language}
  {source_code}
  ```
  
  Phân tích toàn diện theo các bước sau ĐỐI VỚI MÃ NGUỒN GỐC DO NGƯỜI DÙNG CUNG CẤP:
  
  ## 1. Phân tích mã nguồn (Bao quát)
  - Tóm tắt ngắn gọn chức năng hiện tại của mã nguồn và cách tiếp cận của nó
  - Đánh giá mức độ đáp ứng yêu cầu đề bài (đầy đủ, một phần, hoặc không đáp ứng)
  - Phân loại và liệt kê các lỗi theo ba nhóm:
    * Lỗi cú pháp: Những lỗi ngăn code biên dịch/chạy
    * Lỗi logic: Những lỗi làm code hoạt động không chính xác
    * Lỗi tiềm ẩn: Các vấn đề có thể phát sinh trong một số trường hợp đặc biệt
  - Nêu mức độ nghiêm trọng của từng lỗi (nghiêm trọng, trung bình, nhẹ)
  
  ## 2. Phân tích độ phức tạp và hiệu suất
  - Xác định độ phức tạp thời gian của thuật toán (Big O) và tác động đến hiệu suất
  - Phân tích cách sử dụng bộ nhớ và các cơ hội tối ưu hóa
  - Đánh giá khả năng mở rộng với các tập dữ liệu lớn hoặc nhiều trường hợp đặc biệt
  
  ## 3. Gợi ý sửa lỗi chi tiết
  - Phân tích chi tiết từng lỗi, bao gồm cả vị trí chính xác trong code và nguyên nhân cốt lõi
  - Đề xuất cách sửa cụ thể cho từng lỗi với giải thích về cách tiếp cận đã chọn
  - Nêu rõ mức độ ưu tiên cho từng sửa đổi (cần thiết hay tùy chọn)
  - Cung cấp các đoạn mã đã sửa cho mỗi vấn đề, KHÔNG TRẢ TOÀN BỘ MÃ NGUỒN đã sửa trừ khi cần thiết
  
  ## 4. Mô phỏng thực thi từng bước (Sử dụng MÃ NGUỒN GỐC của người dùng)
  ### Trường hợp phát hiện lỗi:
  - Tạo một trường hợp kiểm thử cụ thể (test case) sẽ làm lộ ra lỗi trong mã nguồn gốc
  - Mô phỏng chi tiết quá trình thực thi trên test case đó với:
    * Chỉ rõ giá trị đầu vào
    * Trạng thái các biến quan trọng thay đổi sau mỗi bước
    * Xác định chính xác dòng code gây ra lỗi và giải thích tại sao
  - Nếu không tìm thấy trường hợp lỗi rõ ràng, ghi rõ và cung cấp mô phỏng ngắn gọn

  ### Trường hợp thực thi thành công:
  - Tạo một trường hợp kiểm thử cho mã nguồn gốc hoạt động đúng
  - Mô phỏng chi tiết quá trình thực thi trên test case đó với:
    * Chỉ rõ giá trị đầu vào
    * Trạng thái các biến quan trọng thay đổi sau mỗi bước
    * Giải thích tại sao kết quả thu được là chính xác
  
  ## 5. Đề xuất cải tiến nâng cao
  - Đề xuất các cải tiến tổng thể về thiết kế, cấu trúc và hiệu suất
  - Chỉ ra các kỹ thuật hoặc cấu trúc dữ liệu thay thế có thể cải thiện hiệu suất
  - Đề xuất cách tiếp cận khác (nếu có) có thể giải quyết vấn đề tốt hơn
  - Cung cấp đoạn mã minh họa ngắn gọn cho các đề xuất quan trọng nhất
  
  ## 6. Đánh giá tổng quát và hướng dẫn học tập
  - Đánh giá tổng thể về mã nguồn, bao gồm điểm mạnh và điểm yếu
  - Đề xuất các khái niệm, kỹ thuật hoặc thực hành tốt nhất mà người dùng nên tìm hiểu thêm
  - Gợi ý các tài nguyên học tập phù hợp với trình độ được suy ra từ mã nguồn
  
  **HƯỚNG DẪN TRẢ LỜI - CỰC KỲ QUAN TRỌNG:**
  
  **TOÀN BỘ PHẢN HỒI CỦA BẠN PHẢI LÀ MỘT ĐỐI TƯỢNG JSON HỢP LỆ DUY NHẤT.**
  **KHÔNG BAO GỒM bất kỳ văn bản giới thiệu, giải thích nào, hoặc các dấu markdown code fence (như ```json) trước hoặc sau đối tượng JSON.**
  
  **Yêu cầu chi tiết cho cấu trúc và nội dung JSON:**
  - Tất cả các giá trị chuỗi (string) trong JSON PHẢI được bao quanh bởi dấu ngoặc kép (`"`).
  - Các ký tự đặc biệt trong chuỗi PHẢI được escape đúng cách (dấu ngoặc kép `\"` thành `\\\\\"`, dấu gạch chéo ngược `\\\\` thành `\\\\\\\\`, xuống dòng thành `\\\\n`, tab thành `\\\\t`)
  - Các trường chứa mã nguồn phải là chuỗi JSON được escape đúng cách, KHÔNG sử dụng backtick (`) để bao quanh giá trị
  
  **Cấu trúc JSON bắt buộc:**
  ```json
{json_example_structure}
  ```
  """
  return prompt

# Sửa hàm analyze_code_with_gemini để xử lý JSON đúng cách
def analyze_code_with_gemini(model_name, prompt_text):
  global gemini_model_global
  if not model_name or not gemini_model_global:
    return None, "Model hoặc Gemini client không được cấu hình."
  try:
    generation_config = {
      "temperature": 0.2,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 8192, 
    }
    
    response = gemini_model_global.generate_content(
      prompt_text,
      generation_config=generation_config
    )
    
    response_content = response.text.strip()

    # Logging token usage
    if response.usage_metadata:
        print(f"--- Token Usage for this request ---")
        print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Completion Tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Total Tokens: {response.usage_metadata.total_token_count}")
        print(f"------------------------------------")
    else:
        print("Không có dữ liệu token usage.")


    # 1. Extract JSON string from potential markdown block if present
    #    Or, if the model *only* returns JSON, this step might be bypassed.
    json_str = response_content
    if response_content.startswith("```json") and response_content.endswith("```"):
        json_str = response_content[len("```json"):-(len("```"))].strip()
    elif response_content.startswith("```") and response_content.endswith("```"):
        json_str = response_content[len("```"):-(len("```"))].strip()
    # If it wasn't in a markdown block, we assume json_str is the response_content itself,
    # hoping it's a direct JSON string as per the refined prompt.

    # print(f"---- EXTRACTED/RAW JSON STRING ----\\n{json_str}\\n----------------------------------") # For debugging

    # 2. Attempt to parse the JSON string directly
    try:
        result = json.loads(json_str)
        return result, None
    except json.JSONDecodeError as e_parse:
        # If parsing fails, it means the LLM didn't adhere to the strict JSON prompt
        error_message = f"Lỗi khi phân tích JSON từ phản hồi của Gemini: {str(e_parse)}\\n"
        error_message += f"Phản hồi nhận được (đã cố gắng trích xuất từ markdown nếu có):\\n{json_str}"
        # Include the original full response if it was different (e.g., markdown was stripped)
        if json_str != response_content:
            error_message += f"\\n\\nPhản hồi gốc đầy đủ từ Gemini:\\n{response_content}"
        return None, error_message

  except Exception as e_api_call:
    return None, f"Lỗi khi gọi Gemini API hoặc lỗi không xác định khác: {str(e_api_call)}"

# Convert text to HTML, escaping special characters and preserving line breaks
def text_to_html(text_content):
    if not text_content:
        return ""
    # Convert to string first to handle non-string values (like integers)
    text_content = str(text_content)
    return Markup(text_content.replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;')
                           .replace('\\n', '<br>')
                           .replace('  ', ' &nbsp;'))

# Hiển thị kết quả phân tích - This will now return HTML content or data for a template
# For now, we'll adapt it to be used by the template later, or simplify it.
# The main logic will be in the template itself for display.

@app.route('/', methods=['GET'])
def index():
  if not model_name_global:
    api_status = "API Key không hợp lệ hoặc model không khả dụng. Vui lòng kiểm tra console."
  else:
    api_status = f"API Key hợp lệ. Model: {model_name_global}"
  return render_template('index.html', api_status=api_status)

@app.route('/analyze', methods=['POST'])
def analyze():
  api_key = request.form.get('api_key', '').strip()
  # The following lines related to key validation and consumption have been removed:
  # ok, err = validate_and_consume_key(api_key)
  # if not ok:
  #     return render_template('index.html', error_message=err)
  # keys = load_keys()
  # used = keys.get(api_key, 0)
  # remaining = max(0, 10 - used)

  if not model_name_global:
    return render_template('results.html', error_message="Lỗi: Gemini API chưa được cấu hình đúng.", text_to_html=text_to_html)

  problem_description = request.form.get('problem_description', '')
  source_code = request.form.get('source_code', '')
  language = request.form.get('language', 'Python')

  if not problem_description.strip():
    return render_template('results.html', error_message="Vui lòng nhập đề bài.", text_to_html=text_to_html)
  if not source_code.strip():
    return render_template('results.html', error_message="Vui lòng nhập mã nguồn.", text_to_html=text_to_html)

  # Tạo prompt
  current_prompt = create_prompt(problem_description, source_code, language)
  
  # Gửi đến Gemini API
  result, error = analyze_code_with_gemini(model_name_global, current_prompt)
  
  if error:
    return render_template('results.html', error_message=f"Lỗi phân tích: {error}", text_to_html=text_to_html)
  
  if result:
    return render_template('results.html', result=result, language=language, text_to_html=text_to_html)
  else:
    return render_template('results.html', error_message="Không thể phân tích mã nguồn. Vui lòng thử lại.", text_to_html=text_to_html)

# Đảm bảo Gemini API được khởi tạo dù chạy qua Gunicorn
if not setup_gemini_api():
  # Nếu bạn muốn dừng việc deploy hẳn, uncomment:
  # raise RuntimeError("✖️ Gemini API chưa cấu hình được. Kiểm tra biến GEMINI_API_KEY.")
  print("❌ Lỗi khởi tạo Gemini API; xem log để biết chi tiết.")


# Chạy ứng dụng Flask
if __name__ == "__main__":
  if setup_gemini_api():  # Setup API key and model when app starts
    app.run(debug=True, port=5001)
  else:
    print("Không thể khởi chạy ứng dụng do lỗi cấu hình API. Vui lòng kiểm tra thông báo lỗi ở trên.")
