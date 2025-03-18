from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
from models.exemplosRequest import ExemplosRequest
from models.infoCADto import InfoCADto
from models.requestParaExportarArquivo import RequestParaExportarArquivo
from models.requestParaExportarJson import RequestParaExportarJson
from models.responsesModels import ResponsesModels
from Services.CAService import CAService

router = APIRouter(tags=['Certificado de Aprovação'])
caService = CAService()


@router.get(
    '/CA/{ca}',
    status_code=HTTPStatus.OK,
    summary='Retorna as informações atuais do CA',
    description='Retorna apenas a ultima ocorrencia(dados atuais)',
    responses=ResponsesModels.responsesInfoCA,
    response_model=InfoCADto,
)
async def retornarInfoCA(ca: str):
    dadosEPI = caService.retornarTodasInfoAtuais(ca)
    if dadosEPI is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='CA não encontrado'
        )

    return dadosEPI


@router.get(
    '/retornarTodasAtualizacoes/{ca}',
    status_code=HTTPStatus.OK,
    summary='Retorna as todas as atualizações  CA',
    description='Retorna as todas as atualizações  CA',
    responses=ResponsesModels.responsesInfoCA,
    response_model=list[InfoCADto],
)
async def retornarTodasAtualizacoes(
    ca: str,
):
    dadosEPI = caService.retornarTodasAtualizacoes(ca)
    if dadosEPI is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='CA não encontrado'
        )

    return dadosEPI


@router.get(
    '/validarSituacao/{ca}',
    status_code=HTTPStatus.OK,
    summary='Retorna se o CA está válido',
    description='Retorna se o CA está válido',
)
async def validarCA(ca: str):
    dadosEPI = caService.caValido(ca)
    if dadosEPI is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='CA não encontrado'
        )

    return dadosEPI


@router.post(
    '/exportarExcel',
    summary='Gera um arquivo excel com os CAs informados',
    description='Gera um arquivo excel com os CAs informados, caso algum CA não seja encontrado ocorrerá um erro',
    responses=ResponsesModels.responsesExportar,
)
def exportarExcel(
    request: Annotated[
        RequestParaExportarArquivo, Body(example=ExemplosRequest.exportarArquivo)
    ],
):
    # Criar uma resposta para o arquivo Excel
    if len(request.listaCAs) == 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='A lista de CAs está vazia'
        )
    respExportarExcel = caService.exportarExcel(request.listaCAs, request.nomeArquivo)

    if not respExportarExcel['success']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'CAs não encontrados: {respExportarExcel["CAsNaoEncontrados"]}',
        )

    planilha = respExportarExcel['planilha']

    response = StreamingResponse(
        planilha,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f'attachment; filename={request.nomeArquivo}.xlsx'
        },
    )

    return response


@router.post(
    '/exportarJSON',
    summary='Retorna um JSON com as informações dos CAs informados',
    response_model=list[InfoCADto],
    responses=ResponsesModels.responsesExportar,
)
def exportarJSON(
    request: Annotated[
        RequestParaExportarJson, Body(example=ExemplosRequest.exportarJSON)
    ],
):
    if len(request.listaCAs) == 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='A lista de CAs está vazia'
        )

    respExportarJson = caService.exportarJson(request.listaCAs)

    if not respExportarJson['success']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'CAs não encontrados: {respExportarJson["CAsNaoEncontrados"]}',
        )

    return respExportarJson['JSON']
