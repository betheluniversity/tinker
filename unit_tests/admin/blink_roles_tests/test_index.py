from blink_roles_base import RolesBaseTestCase


class IndexTestCase(RolesBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(IndexTestCase, self).send_get("/admin/blink-roles")
        assert "<h2> Blink Layout Owners </h2>" in response.data

    #     """
    # <form id="blink-login" action="https://blink.bethel.edu/cp/home/login" method="post">
    #     <input id="blink-pass" type="hidden" name="pass" value="p0rt2l" />
    #     <input id="blink-user" type="hidden" name="user" value="" />
    #     <input type="hidden" name="uuid" value="0xACA021" />
    # </form>
    # <script type="text/javascript">
    #     function loadBlinkAccount(ptl, uid){
    #         var submitURL = null;
    #         if(ptl == "Production"){
    #             submitURL = "https://blink.bethel.edu/cp/home/login";
    #         }
    #         else if(ptl == "XP"){
    #             submitURL = "https://blink.xp.bethel.edu/cp/home/login";
    #         }
    #         else if(ptl == "lp4b7"){
    #             submitURL = "https://lp4b7.xp.bethel.edu/cp/home/login";
    #         }
    #         var form = document.getElementById('blink-login');
    #         form.action = submitURL;
    #         document.getElementById('blink-user').value = uid;
    #         form.submit();
    #
    #     }
    #
    # </script>
    # <h2> Blink Layout Owners </h2>
    # <table>
    #     <colgroup>
    #         <col width="33%" class="align-left">
    #         <col width="33%" class="align-left">
    #         <col width="33%" class="align-left">
    #         <col width="1%" class="align-left">
    #     </colgroup>
    #
    #     <tbody>
    #     <tr class="rowheading">
    #         <td colspan="4">
    #             Layout Owner Logins
    #         </td>
    #     </tr>
    #     """ in response.data
