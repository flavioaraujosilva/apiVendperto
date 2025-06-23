from fastapi import FastAPI
import uvicorn

app = FastAPI(title="VendPerto ERP - Teste")

@app.get("/")
def read_root():
    return {"message": "VendPerto ERP funcionando!", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "vendperto-api"}

@app.get("/test")
def test_endpoint():
    return {"test": "API está funcionando perfeitamente", "port": 8001}

if __name__ == "__main__":
    print("🚀 Iniciando VendPerto ERP - Teste Simples")
    print("📡 API estará disponível em: http://localhost:8001")
    print("📖 Documentação em: http://localhost:8001/docs")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False) 