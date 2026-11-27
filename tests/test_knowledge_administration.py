import json
import numpy as np
import pytest
from knowledge.knowledge_database import KnowledgeDatabase
from knowledge.knowledge_manager import KnowledgeManager
from knowledge.administration import KnowledgeAdministration
from knowledge.knowledge_router import KnowledgeRouter

@pytest.fixture
def setup(tmp_path):
    folder=tmp_path/'docs'; folder.mkdir()
    (folder/'a.txt').write_text('Original apple evidence')
    manager=KnowledgeManager(KnowledgeDatabase(tmp_path/'knowledge.db'),folder)
    doc=manager.ingest('a.txt')
    admin=KnowledgeAdministration(manager)
    return folder,manager,admin,doc['id']

def test_update(setup):
    folder,m,a,i=setup
    (folder/'a.txt').write_text('Updated banana evidence')
    a.replace([a.detail(i)])
    assert not m.search('apple') and m.search('banana')
    assert a.detail(i)['id']==i

def test_failed_update(setup):
    folder,m,a,i=setup
    (folder/'a.txt').write_text('')
    with pytest.raises(ValueError): a.replace([a.detail(i)])
    assert m.search('apple')

def test_sync_duplicates(setup):
    folder,m,a,i=setup
    (folder/'b.txt').write_text('Original apple evidence')
    assert a.duplicates()==[['a.txt','b.txt']]
    assert a.sync()['new']==['b.txt']
    (folder/'a.txt').write_text('changed')
    assert a.sync()['modified']==['a.txt']
    (folder/'a.txt').unlink()
    assert a.sync()['missing_or_unreadable']==['a.txt']

def test_backup_restore(setup):
    folder,m,a,i=setup
    name=a.backup()
    a.clear()
    assert m.statistics()['documents']==0 and (folder/'a.txt').exists()
    safety=a.restore(name)
    assert safety in a.backups() and m.search('apple')
    assert 'passed' in a.verify()

def test_restore_invalid(setup):
    folder,m,a,i=setup
    with pytest.raises(ValueError): a.restore('../knowledge.db')
    assert m.search('apple')

def test_export(setup):
    folder,m,a,i=setup
    assert json.loads((a.directory/a.export()).read_text())[0]['id']==i

def test_reindex(setup):
    folder,m,a,i=setup
    store=m.embedding_store()
    class Fake:
        def embed(self,texts):
            v=np.zeros((len(texts),384),dtype=np.float32); v[:,0]=1; return v
    store.engine=Fake()
    a.replace([a.detail(i)],embed=True)
    assert store.statistics()['indexed']==1
    a.replace([a.detail(i)])
    assert store.statistics()['pending']==1

def test_router_confirmation(setup):
    folder,m,a,i=setup
    router=KnowledgeRouter(m)
    assert 'Usage' in router.route('/knowledge-clear')
    assert 'Usage' in router.route('/knowledge-reindex-all')
    assert m.statistics()['documents']==1
    assert 'knowledge-backup' in router.route('/knowledge-help')
