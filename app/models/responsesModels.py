from http import HTTPStatus

from fastapi.responses import JSONResponse
from models.CAsNaoEncontrados import CAsNaoEncontrados
from models.Erros import Erros


class ResponsesModels:
    responsesInfoCA: dict = {
        HTTPStatus.OK.value: {'description': 'Informações do CA'},
        HTTPStatus.NOT_FOUND.value: {
            'model': Erros,
            'description': 'Erros na requisição',
        },
    }
    responsesExportar: dict = {
        HTTPStatus.OK.value: {
            'description': 'Todos CA foram localizados',
            'content': {
                "'application/vnd.      openxmlformats-officedocument.spreadsheetml.sheet": {}
            },
        },
        HTTPStatus.BAD_REQUEST.value: {
            'model': Erros,
            'description': 'listaCAs não pode ser vazia',
        },
        HTTPStatus.NOT_FOUND.value: {
            'model': CAsNaoEncontrados,
            'description': 'Um ou mais CA não foi localizados',
        },
    }

    responsesCANaoEncontrado = JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={'sucess': False, 'erros': ['Numero Ca não encontrado!']},
    )

    responsesListaVazia = JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={'sucess': False, 'erros': ['listaCAs não pode estar vazia']},
    )

    def responsesExportarCAsNaoEncontrado(self, listCAsNaoEncontrados):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={
                'sucess': False,
                'erros': {'CAsNaoEncontrados': listCAsNaoEncontrados},
            },
        )
