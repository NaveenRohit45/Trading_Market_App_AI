window.Dashboard={
widgets:{},
register(name,fn){this.widgets[name]=fn;},
update(name,data){if(this.widgets[name])this.widgets[name](data);},
updateAll(payload){
Object.keys(payload).forEach(k=>this.update(k,payload[k]));
}
};
// Example:
// Dashboard.register("market", d=>console.log(d));
// Dashboard.updateAll(serverPayload);
