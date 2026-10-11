import copy,unittest
from test_original_source_assembly_diagnostic import fixture,evaluate,TOWER
from original_assembly_member_identity import member_identity

class MemberIdentity(unittest.TestCase):
    def test_verified_member_keeps_raw_failures_and_no_installation_credit(self):
        result=evaluate(*fixture());member=member_identity(result,TOWER)
        self.assertTrue(member['proof']['identityAccepted'])
        self.assertEqual(member['rawIndividualIdentity']['reasons'],['full-source-target-coverage'])
        self.assertFalse(member['installationApproved'])
    def test_wrong_member_failed_assembly_and_changed_hash_reject(self):
        result=evaluate(*fixture())
        with self.assertRaises(AssertionError):member_identity(result,'landsd/other:0')
        for key,value in [('passed',False),('reasons',['failed']),('installationApproved',True),('modelGeometryChanges',1)]:
            changed={**result,key:value}
            with self.assertRaises(AssertionError):member_identity(changed,TOWER)
        changed=copy.deepcopy(result);changed['sourceSHA256s'][TOWER]='bad'
        with self.assertRaises(AssertionError):member_identity(changed,TOWER)
    def test_partial_interface_reject(self):
        for key,value in [('strictContacts',5),('wallIntersections',1),('unresolved',[{}])]:
            changed=evaluate(*fixture());changed['strictOriginalInterface']['interface'][key]=value
            with self.assertRaises(AssertionError):member_identity(changed,TOWER)

if __name__=='__main__':unittest.main()
