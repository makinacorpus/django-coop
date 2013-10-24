admin.plugin_coop_newsletter = {
    edit_guests : function(relation_id){
            admin.GET({
                    url : '/wa/action/' + relation_id + '/guest_list/',
            });
    },
}