import pandas as pd

from settings.config import AppConfig

def ler_e_tratar_planejamento(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["FILIAL DESTINO", "CARGA ENTREGA"]].copy()

    # Dic ilial -> box
    filial_para_box = {
        item['Filial']: item['Box']
        for item in AppConfig.DEFAULT_CARGAS_BOX_BR_SAMOR
    }

    df['FILIAL DESTINO'] = pd.to_numeric(
        df['FILIAL DESTINO'],
        errors='coerce'
    )

    df['CARGA ENTREGA'] = pd.to_numeric(
        df['CARGA ENTREGA'],
        errors='coerce'
    )

    df['BOX'] = df['FILIAL DESTINO'].map(filial_para_box)

    df = df.dropna(
        subset=['CARGA ENTREGA']
    )

    df = df.dropna(
        subset=['BOX']
    )

    # Converte para inteiro
    df["FILIAL DESTINO"] = df["FILIAL DESTINO"].astype(int)
    df["CARGA ENTREGA"] = df["CARGA ENTREGA"].astype(int)
    df["BOX"] = df["BOX"].astype(int)

    # Reseta id
    df = df.reset_index(drop=True)

    return df