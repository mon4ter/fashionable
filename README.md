# fashionable
[![PyPI version](https://img.shields.io/pypi/v/fashionable.svg)](https://pypi.org/project/fashionable)
[![Python version](https://img.shields.io/pypi/pyversions/fashionable.svg)](https://pypi.org/project/fashionable)
[![Build Status](https://travis-ci.org/mon4ter/fashionable.svg?branch=master)](https://travis-ci.org/mon4ter/fashionable)
[![codecov](https://codecov.io/gh/mon4ter/fashionable/branch/master/graph/badge.svg)](https://codecov.io/gh/mon4ter/fashionable)

Decorate your project with some fashionable supermodels.

### Decorator example
```python
from typing import Set

from fashionable import fashionable

@fashionable
def bits_to_binary_like(bits: Set[int], length: int = 8) -> int:
    bits.add(0)
    return ''.join(str(int(b in bits)) for b in range(length, 0, -1))

bits_to_binary_like('334455')  # 11100
```

### Model example
```python
from typing import List, Optional

from fashionable import Attribute, Model


class Project(Model):
    id = Attribute(str, max=32)
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
    id = Attribute(str, max=32)
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
    return json(project)


@app.post('/project')
async def project_create(request):
    project = await Project.create(**request.json)
    return json(
        project,
        status=201,
        headers={'Location': '/project/' + project.id},
    )


@app.put('/project/<id_>')
async def project_update(request, id_):
    project = await Project.get(id_, fresh=True)
    await project.update(**request.json)
    return json(project)


@app.delete('/project/<id_>')
async def project_delete(request, id_):
    project = await Project.get(id_, fresh=True)
    await project.delete()
    return HTTPResponse(status=204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```
