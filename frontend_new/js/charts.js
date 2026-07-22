window.Charts={
instances:{},
register(id,chart){this.instances[id]=chart;},
update(id,data){
const c=this.instances[id];
if(c&&typeof c.updateSeries==="function"){c.updateSeries(data);}
},
destroy(id){
if(this.instances[id]?.destroy)this.instances[id].destroy();
delete this.instances[id];
}
};
// Supports ApexCharts/Lightweight Charts wrapper integration.
