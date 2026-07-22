window.Theme={
set(mode){document.documentElement.setAttribute("data-theme",mode);localStorage.theme=mode;},
load(){this.set(localStorage.theme||"dark");},
toggle(){this.set((localStorage.theme||"dark")==="dark"?"light":"dark");}
};