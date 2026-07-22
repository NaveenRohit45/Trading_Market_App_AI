class TradingWebSocket{
constructor(url){
this.url=url;
this.ws=null;
this.handlers={};
this.reconnectDelay=3000;
}
connect(){
this.ws=new WebSocket(this.url);
this.ws.onopen=()=>this.emit("open");
this.ws.onmessage=(e)=>{
try{
const data=JSON.parse(e.data);
this.emit("message",data);
if(data.type)this.emit(data.type,data.payload);
}catch(err){console.error(err);}
};
this.ws.onclose=()=>{
this.emit("close");
setTimeout(()=>this.connect(),this.reconnectDelay);
};
this.ws.onerror=(e)=>this.emit("error",e);
}
send(data){
if(this.ws&&this.ws.readyState===WebSocket.OPEN){
this.ws.send(JSON.stringify(data));
}
}
on(event,callback){
(this.handlers[event]??=[]).push(callback);
}
emit(event,data){
(this.handlers[event]||[]).forEach(cb=>cb(data));
}
disconnect(){
if(this.ws)this.ws.close();
}
}
window.TradingWebSocket=TradingWebSocket;

// Example:
// const socket=new TradingWebSocket("ws://localhost:8000/ws");
// socket.on("market",payload=>console.log(payload));
// socket.connect();
