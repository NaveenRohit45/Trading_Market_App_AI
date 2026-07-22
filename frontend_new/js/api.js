window.API={
baseUrl:"http://127.0.0.1:8000",
async get(path){return fetch(this.baseUrl+path).then(r=>r.json())},
async post(path,data){return fetch(this.baseUrl+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}).then(r=>r.json())}
};