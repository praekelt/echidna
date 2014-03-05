(function (exports) {


    function debug (d) {
        console.log("DEBUG: " + d);
    };


    function EchidnaPublisher ($publish_form, api_server) {
        var self = this;

        self.api_server = api_server;
        self.$publish_form = $publish_form;

        self.btn = null;
        self.text = null;

        self.init = function () {
            self.btn = self.$publish_form.find(".echidna-publish-btn");
            self.text = self.$publish_form.find(".echidna-publish-text");
            self.btn.on("click", self.on_publish);
        };

        self.post = function (channel, msg) {
            debug("Publishing to " + channel + " ...");
            debug(JSON.stringify(msg));

            var xhdr = $.post(
                "http://" + self.api_server + "/publish/" + channel + "/",
                JSON.stringify(msg)
            ).done(function (data, status) {
                debug("Published successfully.");
            }).fail(function () {
                debug("Publishing failed. :/");
            });
        };

        self.on_publish = function () {
            var text = self.text.val().trim(),
                msg = null;

            if (text) {
                msg = {
                    created: $.now(),
                    text: text,
                }
                self.post("radio_ga_ga", msg);
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
            self.send_msg({
                "msg_type": "subscribe",
                "channel": "radio_ga_ga",
            });
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


    function EchidnaReceiver ($msg_list) {
        var self = this;

        self.$msg_list = $msg_list;

        self.msgs = null;

        self.init = function () {
            self.msgs = [];
        };

        self.on_msg = function(msg) {
            var handler = self["on_" + msg.msg_type];
            if (!handler) {
                handler = self.on_invalid;
            }
            handler(msg);
        };

        self.on_card = function (msg) {
            if (self.msgs.length == 0) {
                self.$msg_list.empty();
            }
            self.msgs.push(msg);
            var card = msg.card;
            var channel = msg.channel;
            var created = moment(card.created).format("MMMM Do YYYY, h:mm:ss a");
            self.$msg_list.prepend(
                '<li class="list-group-item">' +
                    '<span class="badge">' + created + '</span>' +
                    '<span class="badge">' + channel + '</span>' +
                    card.text +
                    '</li>'
            );
        };

        self.on_error = function(msg) {
            debug("ERROR msg: " + JSON.stringify(msg));
        };

        self.on_invalid = function (msg) {
            debug("INVALID msg: " + JSON.stringify(msg));
        };

        self.init();
    }

    exports.EchidnaPublisher = EchidnaPublisher;
    exports.EchidnaWebSocket = EchidnaWebSocket;
    exports.EchidnaReceiver = EchidnaReceiver;

})(window.echidna = window.echidna || {});