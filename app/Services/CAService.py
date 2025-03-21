import io
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from Services.BaseDadosCaEPI import BaseDadosCaEPI


class CAService:
    def __init__(self):
        self.lock = threading.Lock()
        self.baseDadosProvider = BaseDadosCaEPI()
        self.baseDadosDF = self.baseDadosProvider.retornarBaseDados()
        self.horaAtualizacao = 12
        self.minutoAtualizacao = 13
        self._defineHorarioAtualizacao()

    def retornarTodasAtualizacoes(self, ca: str) -> list[dict] | None:
        dadosEPI = self.baseDadosDF.loc[self.baseDadosDF['RegistroCA'] == ca]
        if dadosEPI.empty:
            return None
        return dadosEPI.to_dict('records')

    def retornarTodasInfoAtuais(self, ca: str) -> dict | None:
        dadosEPI = self.baseDadosDF.loc[self.baseDadosDF['RegistroCA'] == ca]
        if dadosEPI.empty:
            return None

        return dadosEPI.iloc[-1].to_dict()

    def caValido(self, ca) -> bool:
        ca_info = self.retornarTodasInfoAtuais(ca)

        return ca_info is not None and ca_info['Situacao'] == 'VÁLIDO'

    def exportarExcel(self, listaCAs: list[str], nomeArquivo: str) -> dict:
        df = self._filtrarPorCAs(listaCAs)

        CAsNaoEncontrados = self._retornaCAsNaoEncontrado(df, listaCAs)
        if CAsNaoEncontrados != []:
            return {'success': False, 'CAsNaoEncontrados': CAsNaoEncontrados}

        # Converter o dataframe para um objeto Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=nomeArquivo)
        output.seek(0)

        return {'success': True, 'planilha': output}

    def exportarJson(self, listaCAs: list[str]) -> dict:
        df = self._filtrarPorCAs(listaCAs)
        CAsNaoEncontrados = self._retornaCAsNaoEncontrado(df, listaCAs)
        if CAsNaoEncontrados != []:
            return {'success': False, 'CAsNaoEncontrados': CAsNaoEncontrados}

        return {'success': True, 'JSON': df.to_dict('records')}

    def _filtrarPorCAs(self, listaCAs: list[str]) -> pd.DataFrame:
        with self.lock:
            df = self.baseDadosDF.loc[self.baseDadosDF['RegistroCA'].isin(listaCAs)]
        return df.drop_duplicates('RegistroCA', keep='last')

    def _retornaCAsNaoEncontrado(
        self, df: pd.DataFrame, listaCAs: list[str]
    ) -> list[str]:
        return [ca for ca in listaCAs if ca not in df['RegistroCA'].values]

    def _atualizarBaseDados(self):
        with self.lock:
            base = self.baseDadosProvider
            self.baseDadosDF = base.retornarBaseDados()
            print('Base de Dados atualizada em', datetime.now())

    def _defineHorarioAtualizacao(self):
        scheduler = BackgroundScheduler(timezone=ZoneInfo('America/Sao_Paulo'))
        scheduler.start()

        # É atualizado as 20h, mas resolvi dar uma margem de erro
        scheduler.add_job(
            self._atualizarBaseDados,
            'cron',
            hour=self.horaAtualizacao,
            minute=self.minutoAtualizacao,
            day_of_week='0-6',
        )
