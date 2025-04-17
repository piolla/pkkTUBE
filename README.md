# YouTube MCP Agent 
- YouTube 검색, 요약, 채널 분석등을 위한 Youtube MCP Agent구현 예제.
- Youtube 로 검색하고, 요약등의 작업 History file을 저장하고 저장한 데이터 기반으로 Youtube 검색기능


### 1. 설치단계  
1) Repository clone 또는 다운로드하기
2) Openai API Key 발급
3) Youtube data API Key 발급
4) Python 가상환경 설정
5) Package 설치
6) Client 연결을 위한 Python, MCP Server Script 경로 설정(JSON)   


### 1-1. Repository clone 또는 다운로드하기
```shell
git clone https://github.com/piolla/pkkTUBE
cd pkkTUBE
```

### 1-2. Openai API Key 발급 
https://platform.openai.com/api-keys 

### 1-3. Youtube API Key 발급 
https://console.cloud.google.com/welcome?hl=ko&pli=1&project=prismatic-vial-371401

### 1-4. Python 가상환경 설정 
- 가상환경 만들기:

### 1-5. Package 설치 
```shell
    pip install mcp openai-agents streamlit youtube-transcript-api python-dotenv
```

### 1-6. Client 연결을 위한 Python, MCP Server Script 경로 설정(JSON)  
```json
{
    "mcpServers": {
      "mcp-test": {
        "command": "C:\\Users\\cnext\\anaconda3\\envs\\aria\\python.exe",
        "args": [
          "C:\\Users\\cnext\\PiollaPrograms\\AI_Programs\\MCP\\YouTubeAgent\\2_mcp_server.py"
        ]
      }
    }
  }
```
### Files
```script
~~/MCP-pkkTube/.env 
             /.env.example 
             /pkkTubeCli3.py 
	     /pkkTubeServer.py 
	     /pkkTube.json 
	     /chat_histories/chat_2025-04-13.json 
	     /chat_histories/chat_2025-04-14.json 
```
