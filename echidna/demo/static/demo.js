(function (exports) {


    function debug (d) {
        console.log("DEBUG: " + d);
    };


    function EchidnaPublisher (publish_form_id, api_server) {
        var self = this;

        self.api_server = api_server;
        self.publish_form_id = publish_form_id;

        self.btn = null;
        self.text = null;

        self.init = function () {
            self.btn = $("#publish-form .echidna-publish-btn");
            self.text = $("#publish-form .echidna-publish-text");
            self.btn.on("click", self.on_publish);
        };

        self.on_publish = function () {
            var text = self.text.val().trim(),
                msg = null;

            if (text) {
                msg = {
                    created: $.now(),
                    text: text,
                }
                debug("TODO: AJAX post msg")
                debug("Published: " + JSON.stringify(msg));
            }

            self.text.val("");
        };

        self.init();
    }


    function EchidnaWebSocket (receiver, api_server) {
        var self = this;

        self.receiver = receiver;
        self.api_server = api_server;

        self.server = null;

        self.init = function () {
            var server = new WebSocket("ws://" + self.api_server + "/subscribe");
            self.server = server;
            server.onopen = self.on_open;
            server.onclose = self.on_close;
            server.onmessage = self.on_message;
            server.onerror = self.on_error;
        };

        self.send_msg = function (msg) {
            self.server.send(JSON.stringify(msg));
        };

        self.on_open = function () {
            debug("connected");
        };

        self.on_close = function () {
            debug("connected");
        };

        self.on_message = function (event) {
            debug("received: " + event.data);
            var msg = JSON.parse(event.data);
            self.receiver.on_msg(msg);
        };

        self.on_error = function (e) {
            debug(e);
        };

        self.init();
    }


    function EchidnaReceiver (msg_list_id) {
        var self = this;

        self.msg_list_id = msg_list_id;

        self.msg_list = null;
        self.msgs = null;

        self.init = function () {
            self.msg_list = $("#received-list");
            self.msgs = [];
        };

        self.on_msg = function (msg) {
            if (self.msgs.length == 0) {
                self.msg_list.empty();
            }
            self.msgs.push(msg);
            var created = moment(msg.created).format("MMMM Do YYYY, h:mm:ss a");
            self.msg_list.prepend(
                '<li class="list-group-item">' +
                    '<span class="badge">' + created + '</span>' +
                    msg.text +
                    '</li>'
            );
        };

        self.init();
    }

    exports.EchidnaPublisher = EchidnaPublisher;
    exports.EchidnaWebSocket = EchidnaWebSocket;
    exports.EchidnaReceiver = EchidnaReceiver;

})(window.echidna = window.echidna || {});