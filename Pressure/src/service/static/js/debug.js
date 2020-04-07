var debugInfo = new Vue({
    el: "#debugDiv",

    data: {
        taskList: [],
        hostList: [],
        option: "",
    },

    ready: function() {
        this.getTaskList();
        this.getHostList();
    },

    methods: {
        getTaskList: function() {
            this.$http.get("/taskList").then((response)=>{
                var jsonData = JSON.parse(response.data);
                this.taskList = jsonData.res;
            }, (response) => {
                console.log(response);
            });
        },

        getHostList: function() {
            this.$http.get("/resource").then((response)=>{
                var jsonData = JSON.parse(response.data);
                this.hostList = jsonData.res;
            }, (response) => {
                console.log(response);
            });
        },

        shortPath: function(path) {
            var index = path.lastIndexOf("/");
            return path.substring(index+1);
        },

        setOption: function(option) {
            this.option = option;
        }
    }

})
