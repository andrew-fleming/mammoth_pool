import pytest
import asyncio
import os
from starkware.starknet.testing.starknet import Starknet
from utils import Signer, to_uint, str_to_felt
from dotenv import load_dotenv

load_dotenv()

KEY = int(os.getenv("PRIVATE_KEY"))
signer = Signer(KEY)


@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture(scope='module')
async def token_factory():
    starknet = await Starknet.empty()
    owner = await starknet.deploy(
        "contracts/Account.cairo",
        constructor_calldata=[signer.public_key]
    )

    proxy = await starknet.deploy(
        "contracts/mammoth/mammoth_proxy.cairo",
        constructor_calldata=[owner.contract_address]
    )

    pool = await starknet.deploy(
        "contracts/mammoth/mammoth_pool.cairo",
        constructor_calldata=[proxy.contract_address]
    )

    lp = await starknet.deploy(
        "contracts/mammoth/mammoth_token.cairo",
        constructor_calldata=[
            str_to_felt("MAMMOTH_LP"),
            str_to_felt("MLP"),
            proxy.contract_address
        ]
    )

    tusdc = await starknet.deploy(
        "contracts/token/ERC20_Mintable.cairo",
        constructor_calldata=[
            str_to_felt("testUSDC"),
            str_to_felt("TUSDC"),
            *to_uint(0),
            owner.contract_address,
            pool.contract_address
        ]
    )

    fc = await starknet.deploy(
        "contracts/token/ERC20_Mintable.cairo",
        constructor_calldata=[
            str_to_felt("FantieCoin"),
            str_to_felt("FC"),
            *to_uint(0),
            owner.contract_address,
            pool.contract_address
        ]
    )

    teeth = await starknet.deploy(
        "contracts/token/ERC20_Mintable.cairo",
        constructor_calldata=[
            str_to_felt("testETH"),
            str_to_felt("TEETH"),
            *to_uint(0),
            owner.contract_address,
            pool.contract_address]
    )
    return owner, proxy, pool, lp, tusdc, fc, teeth


@pytest.mark.asyncio
async def test_initializer(token_factory):
    owner, _, _, _, _, _, _ = token_factory

    execution_info = await owner.get_public_key().invoke()
    assert execution_info.result == (signer.public_key,)


@pytest.mark.asyncio
async def test_create_pool(token_factory):
    owner, proxy, pool, lp, _, _, _ = token_factory

    swap_fee = (1, 1000)
    exit_fee = (1, 1000)

    await signer.send_transaction(owner, proxy.contract_address, 'create_pool', [
        lp.contract_address,
        pool.contract_address,
        *swap_fee,
        *exit_fee
    ])


@pytest.mark.asyncio
async def test_add_erc20s(token_factory):
    owner, proxy, pool, _, tusdc, fc, teeth = token_factory

    weight = (1, 3)
    tokens = [tusdc, fc, teeth]

    for token in tokens:
        await signer.send_transaction(
            owner, proxy.contract_address, 'add_approved_erc20_for_pool', [
                pool.contract_address,
                token.contract_address,
                *weight
            ]
        )
