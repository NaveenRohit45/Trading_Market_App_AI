window.LiveAI={
start(socket){
socket.on("prediction",p=>console.log("AI Prediction",p));
socket.on("decision",d=>console.log("Decision",d));
socket.on("alert",a=>console.log("Alert",a));
}
};