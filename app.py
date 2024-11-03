from flask import Flask, render_template, request, Response, jsonify
from models.zhipu_model import ZhipuModel
import json

app = Flask(__name__)
zhipu_model = ZhipuModel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET'])
def submit():
    data = json.loads(request.args.get('data', '{}'))
    
    def generate_response():
        try:
            model = ZhipuModel()
            print("开始生成三个主要方案...")
            
            # 首先并行处理三个主要方案
            responses = model.process_parallel_responses(data)
            print(responses)
            
            # 用于跟踪每个流的完成状态和累积内容
            completed = {k: False for k in responses.keys()}
            accumulated = {k: "" for k in responses.keys()}
            
            # 处理三个主要方案
            while not all(completed.values()):
                for response_type, response in responses.items():
                    if not completed[response_type]:
                        try:
                            chunk = next(response)
                            if hasattr(chunk.choices[0].delta, 'content'):
                                content = chunk.choices[0].delta.content
                                if content:
                                    accumulated[response_type] += content
                                    yield f"data: {json.dumps({response_type: content})}\n\n"
                        except StopIteration:
                            completed[response_type] = True
                            print(f"{response_type} 完成生成")
            
            print("所有主要方案完成，开始生成综合建议...")
            
            # 所有主要方案完成后，生成综合建议
            summary_prompt = f"""
            基于用户信息：
            {model._format_user_info(data)}
            
            以及已生成的建议：
            
            营养补充方案：
            {accumulated['supplement']}
            
            中医调理方案：
            {accumulated['tcm']}
            
            饮食方案：
            {accumulated['diet']}
            
            请提供一份整体的综合建议，总结以上三个方案的要点，并给出统筹安排的建议，并制定周一到周日的饮食计划。
            """
            
            print("开始请求综合建议...")
            
            # 生成综合建议
            summary_response = model.get_response([{"role": "user", "content": summary_prompt}])
            
            print("开始流式输出综合建议...")
            
            # 流式输出综合建议
            for chunk in summary_response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        #print(f"输出综合建议片段: {content[:20]}...")
                        yield f"data: {json.dumps({'summary': content})}\n\n"
            
            print("综合建议生成完成")
            
            # 发送完成事件
            yield "event: complete\ndata: {}\n\n"
                            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        generate_response(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/analyze', methods=['POST'])
def analyze():
    # 处理POST请求的逻辑
    return jsonify({'message': 'Analysis complete'})

#if __name__ == '__main__':
 #   app.run(debug=True)
