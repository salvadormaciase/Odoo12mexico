odoo.define("l10n_mx_portal.tour_download_zipped_cfdi", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    tour.register("check_download_zipped_cfdi", {
        test: true,
        wait_for: base.ready(),
    },
    [
        {
            trigger: 'a.btn-download-zip-cfdi',
            content: "Click on DOWNLOAD ZIP",
            run: "click",
        },
    ]);
});
