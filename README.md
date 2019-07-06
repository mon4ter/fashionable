# fashionable
Decorate your project with some fashionable supermodels.

### Model example
```python
from typing import List, Optional

from fashionable import Attribute, Model


class Project(Model):
    id = Attribute(str, limit=32)
    name = Attribute(str)
    organization = Attribute(Optional[str])
    domain = Attribute(Optional[str])
    links = Attribute(Optional[List[str]])
    
project = Project(1, 'Test')
```

### Supermodel example with Sanic
```python
from typing import List, Optional

from fashionable import Attribute, Supermodel
from sanic import Sanic
from sanic.response import json, HTTPResponse

app = Sanic()
app.db = ...

class Project(Supermodel):
    _ttl = 300
    id = Attribute(str, limit=32)
    name = Attribute(str)
    organization = Attribute(Optional[str])
    domain = Attribute(Optional[str])
    links = Attribute(Optional[List[str]])
    
    @staticmethod
    async def _create(raw: dict):
        await app.db.project_create(raw)

    @staticmethod
    async def _get(id_: str) -> Optional[dict]:
        return await app.db.project_get(id_)

    @staticmethod
    async def _update(id_: str, raw: dict):
        await app.db.project_update(id_, raw)

    @staticmethod
    async def _delete(id_: str):
        await app.db.project_delete(id_)


@app.get('/project/<id_>')
async def project_get(request, id_):
    project = await Project.get(id_)
    return json(dict(project))


@app.post('/project')
async def project_create(request):
    project = await Project.create(**request.json)
    return json(
        dict(project),
        status=201,
        headers={'Location': '/project/' + project.id},
    )


@app.put('/project/<id_>')
async def project_update(request, id_):
    project = await Project.get(id_, fresh=True)
    await project.update(**request.json)
    return json(dict(project))


@app.delete('/project/<id_>')
async def project_delete(request, id_):
    project = await Project.get(id_, fresh=True)
    await project.delete()
    return HTTPResponse(status=204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```