# implements the following:
#
# ON POOL
# call_deposit  
# call_withdraw

%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from contracts.lib.openzeppelin.contracts.utils.constants import TRUE, FALSE

@contract_interface
namespace IPoolContract:
    func deposit(amount: Uint256, address: felt, erc20_address: felt) -> (success: felt):
    end

    func withdraw(amount: Uint256, address: felt, erc20_address: felt) -> (success: felt):
    end

    func swap(amount: Uint256, address: felt, erc20_address_in: felt, erc20_address_out: felt) -> (success: felt):
    end

    func get_ERC20_balance(erc20_address: felt) -> (res: Uint256):
    end
end

@contract_interface
namespace IPoolRegister:
    func Register_initialize_pool(lp_address: felt, s_fee: Ratio, e_fee: Ratio, erc_list_len: felt, erc_list: ApprovedERC20*) -> (bool: felt):
    end
end

#store the address of the pool contract
@storage_var
func approved_pool_address(pool_address: felt) -> (bool: felt):
end

func Router_call_deposit{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(amount: felt, address: felt, pool_address: felt, erc20_address: felt) -> (success: felt):
    alloc_locals
    let (local success: felt) = IPoolContract.deposit(contract_address=pool_address, amount=amount, address=address, erc20_address=erc20_address)
    assert success = TRUE
    return (TRUE)
end

func Router_call_withdraw{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(amount: felt, address: felt, pool_address: felt, erc20_address: felt) -> (success: felt):
    let (local success: felt) = IPoolContract.withdraw(contract_address=pool_address, amount=amount, address=address, erc20_address=erc20_address)
    assert success = TRUE
    return (TRUE)
end

func Router_call_swap{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(amount: felt, address: felt, pool_address: felt, erc20_address_in: felt, erc20_address_out: felt) -> (success: felt):
    let (local success: felt) = IPoolContract.swap(contract_address=pool_address, amount=amount, address=address, erc20_address_in=erc20_address_in, erc20_address_out=erc20_address_out)
    assert success = TRUE
    return (TRUE)
end

func Router_create_pool{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(pool_address: felt, s_fee: Ratio, e_fee: Ratio, erc_list_len: felt, erc_list: ApprovedERC20*) -> (bool: felt):
    alloc_locals
    approved_pool_address.write(pool_address, TRUE)
    let (local success: felt) = IPoolRegister.Register_initialize_pool(contract_address=pool_address, s_fee=s_fee, e_fee=e_fee, erc_list_len=erc_list_len, erc_list=erc_list)
    assert success = TRUE
    return (TRUE)
end

func Router_only_approved_pool{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(pool_address: felt):
    alloc_locals

    local approved: felt = approved_pool_address.read(pool_address)
    assert approved = TRUE

    return ()
end
