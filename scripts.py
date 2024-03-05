#!/usr/bin/python3

# This is the homework submission file for the BTC Scripting homework, which
# can be found at http://aaronbloomfield.github.io/ccc/hws/btcscript.  That
# page describes how to fill in this program.

from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress
from bitcoin import SelectParams
from bitcoin.core import CMutableTransaction
from bitcoin.core.script import *
from bitcoin.core import x
import random


#------------------------------------------------------------
# Do not touch: change nothing in this section!

# ensure we are using the bitcoin testnet and not the real bitcoin network
SelectParams('testnet')

# The address that we will pay our tBTC to -- do not change this!
tbtc_return_address = CBitcoinAddress('mohjSavDdQYHRYXcS3uS6ttaHP8amyvX78') # https://testnet-faucet.com/btc-testnet/

# The address that we will pay our BCY to -- do not change this!
bcy_dest_address = CBitcoinAddress('mgBT4ViPjTTcbnLn9SFKBRfGtBGsmaqsZz')

# Yes, we want to broadcast transactions
broadcast_transactions = True

# Ensure we don't call this directly
if __name__ == '__main__':
    print("This script is not meant to be called directly -- call bitcoinctl.py instead")
    exit()


#------------------------------------------------------------
# Setup: your information

# Your UVA userid
userid = 'qbw2cx'

# Enter the BTC private key and invoice address from the setup 'Testnet Setup'
# section of the assignment.  
my_private_key_str = "cUbNTZfMojKTFUqQdg25v7QU8uLgmquRW51CtxezMEC4FG9D7vM9"
my_invoice_address_str = "n1SPo6gaK4vRouaFDKzJ7PhUH28jd5ssN9"

# Enter the transaction ids (TXID) from the funding part of the 'Testnet
# Setup' section of the assignment.  Each of these was provided from a faucet
# call.  And obviously replace the empty string in the list with the first
# one you obtain..
txid_funding_list = ["f97063ebb81cd0ce3be6c8ec78a2f523c8bba93a60cdb892c35fb1241186f1dd", "4ab62bf8594f075b8092e38393e2c0f860f77da00ab4132aa0cc63b9d57d9418", "58ddf75854aa927fc66fb45f7c9c3636827c544ccecd4d2e99bd3352e7441748"]

# These conversions are so that you can use them more easily in the functions
# below -- don't change these two lines.
if my_private_key_str != "":
    my_private_key = CBitcoinSecret(my_private_key_str)
    my_public_key = my_private_key.pub


#------------------------------------------------------------
# Utility function(s)

# This function will create a signature of a given transaction.  The
# transaction itself is passed in via the first three parameters, and the key
# to sign it with is the last parameter.  The parameters are:
# - txin: the transaction input of the transaction being signed; type: CMutableTxIn
# - txout: the transaction output of the transaction being signed; type: CMutableTxOut
# - txin_scriptPubKey: the pubKey script of the transaction being signed; type: list
# - private_key: the private key to sign the transaction; type: CBitcoinSecret
def create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, private_key):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    return private_key.sign(sighash) + bytes([SIGHASH_ALL])


#------------------------------------------------------------
# Testnet Setup: splitting coins

# The transaction ID that is to be split -- the assumption is that it is the
# transaction hash, above, that funded your account with tBTC.  You may have
# to split multiple UTXOs, so if you are splitting a different faucet
# transaction, then change this appropriately. It must have been paid to the
# address that corresponds to the private key above
txid_split = txid_funding_list[2]

# After all the splits, you should have around 10 (or more) UTXOs, all for the
# amount specified in this variable. That amount should not be less than
# 0.0001 BTC, and can be greater.  It will make your life easier if each
# amount is a negative power of 10, but that's not required.
split_amount_to_split = 0.0005209

# How much BTC is in that UTXO; look this up on https://live.blockcypher.com
# to get the correct amount.
split_amount_after_split = 0.0001

# How many UTXO indices to split it into -- you should not have to change
# this!  Note that it will actually split into one less, and use the last one
# as the transaction fee.
split_into_n = int(split_amount_to_split/split_amount_after_split)

# The transaction IDs obtained after successfully splitting the tBTC.
txid_split_list = ["3e5377425df61472939aa1d31ce65f718a6e096d3593a099e5f62f9bc880bba2", "0fa837360f22ea49190167f3c6e5d707462644379140ff6f2377cf83e962c87a", "fc6c5c32a58e4c7ab0b94754c0bf7860334ebbc6f425372b433f1282b980cebe"]


#------------------------------------------------------------
# Global settings: some of these will need to be changed for EACH RUN

# The transaction ID that is being redeemed for the various parts herein --
# this should be the result of the split transaction, above; thus, the
# default is probably sufficient.
txid_utxo = txid_split_list[2]

# This is likely not needed.  The bitcoinctl.py will take a second
# command-line parmaeter, which will override this value.  You should use the
# second command-line parameter rather than this variable. The index of the
# UTXO that is being spent -- note that these indices are indexed from 0.
# Note that you will have to change this for EACH run, as once a UTXO index
# is spent, it can't be spent again.  If there is only one index, then this
# should be set to 0.
utxo_index = -1

# How much tBTC to send -- this should be LESS THAN the amount in that
# particular UTXO index -- if it's not less than the amount in the UTXO, then
# there is no miner fee, and it will not be mined into a block.  Setting it
# to 90% of the value of the UTXO index is reasonable.  Note that the amount
# in a UTXO index is split_amount_to_split / split_into_n.
send_amount = split_amount_after_split * 0.9


#------------------------------------------------------------
# Part 1: P2PKH transaction

# This defines the pubkey script (aka output script) for the transaction you
# are creating.  This should be a standard P2PKH script.  The parameter is:
# - address: the address this transaction is being paid to; type:
#   P2PKHBitcoinAddress
def P2PKH_scriptPubKey(address):
    return [
        OP_DUP,
        OP_HASH160,
        address,
        OP_EQUALVERIFY,
        OP_CHECKSIG
    ]

# This function provides the sigscript (aka input script) for the transaction
# that is being redeemed.  This is for a standard P2PKH script.  The
# parameters are:
# - txin: the transaction input of the UTXO being redeemed; type:
#   CMutableTxIn
# - txout: the transaction output of the UTXO being redeemed; type:
#   CMutableTxOut
# - txin_scriptPubKey: the pubKey script (aka output script) of the UTXO being
#   redeemed; type: list
# - private_key: the private key of the redeemer of the UTXO; type:
#   CBitcoinSecret
def P2PKH_scriptSig(txin, txout, txin_scriptPubKey, private_key):
    signature = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, private_key)
    pubkey = private_key.pub
    return [ 
             signature, pubkey
           ]

# The transaction hash received after the successful execution of this part
#USING UTXO 0
txid_p2pkh = "be44a31dae3916f5e3884458e95828ccd0ee4013f38ba73b37dfd5609bf99bd4"


#------------------------------------------------------------
# Part 2: puzzle transaction

# These two values are constants that you should choose -- they should be four
# digits long.  They need to allow for only integer solutions to the linear
# equations specified in the assignment.
puzzle_txn_p = 7663
puzzle_txn_q = 5727

# These are the solutions to the linear equations specified in the homework
# assignment.  You can use an online linear equation solver to find the
# solutions.
puzzle_txn_x = 1936
puzzle_txn_y = 3791

# This function provides the pubKey script (aka output script) that requres a
# solution to the above equations to redeem this UTXO.
#USED UTXO 1 AND 2
def puzzle_scriptPubKey():
    return [ 
            #y, x
            OP_OVER, #y, x, y
            OP_OVER, #y, x, y, x
            OP_DUP, #y, x, y, x, x
            OP_ADD, #y, x, y, 2x
            OP_ADD, #y, x, 2x + y
            puzzle_txn_p, #y, x, 2x + y, p
            OP_EQUALVERIFY, #verify 2x + y = p
            OP_ADD, #y + x
            puzzle_txn_q, #y + x, q
            OP_EQUAL #(1...?)
           ]    

# This function provides the sigscript (aka input script) for the transaction
# that you are redeeming.  It should only provide the two values x and y, but
# in the order of your choice.
def puzzle_scriptSig():
    return [ 
            puzzle_txn_y, puzzle_txn_x
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 2a)
txid_puzzle_txn1 = "6551ff0a63f25850c1e9ae79aaddf4d802564365f7954db97f8eb615564b96cd"

# The transaction hash received after successfully submitting the second
# transaction above (part 2b)
txid_puzzle_txn2 = "869667f9576f5a93118aff14f82235c56f9caef1cefd00033d0715f35ce37544"


#------------------------------------------------------------
# Part 3: Multi-signature transaction
#UTXO 3 (LAST ONE FOR FIRST SPLIT)

# These are the public and private keys that need to be created for alice,
# bob, and charlie
alice_private_key_str = "cNe7ztEjQppR4uyxXKyr4feAfL3jCbp2XwaeFAHwNcL9nDVaUyRy"
alice_invoice_address_str = "mrnFvPdgzy2uAxDGN98XJqQQ88V672w9Zb"
bob_private_key_str = "cPnbkGnPDL9jxLPKoweDXM1rtNtmN7bNeNvMeEXg8VHYK3xax3BR"
bob_invoice_address_str = "mprWtJZjfvZEHbkRq4fhpHBtKhVqksSWNk"
charlie_private_key_str = "cSw7zU712Uk54HAZBsmxfWd4cjRjYJecKZ6bx6S9tqnqKzfjUw8r"
charlie_invoice_address_str = "mmBkbctKmK3UPsftBqez9aDKSfQP1Etp7F"

# These three lines convert the above strings into the type that is usable in
# a script -- you should NOT modify these lines.
if alice_private_key_str != "":
    alice_private_key = CBitcoinSecret(alice_private_key_str)
if bob_private_key_str != "":
    bob_private_key = CBitcoinSecret(bob_private_key_str)
if charlie_private_key_str != "":
    charlie_private_key = CBitcoinSecret(charlie_private_key_str)

# This function provides the pubKey script (aka output script) that will
# require multiple different keys to allow redeeming this UTXO.  It MUST use
# the OP_CHECKMULTISIGVERIFY opcode.  While there are no parameters to the
# function, you should use the keys above for alice, bob, and charlie, as
# well as your own key.
def multisig_scriptPubKey():
    return [ 
            #bankSig, 0, sig1, sig2, 2
            alice_private_key.pub,
            bob_private_key.pub,
            charlie_private_key.pub,
            OP_3, #bankSig, 0, sig1, sig2, 2, alicePub, bobPub, charliePub, 3
            OP_CHECKMULTISIGVERIFY, #bankSig
            my_private_key.pub, #0, bankSig, bankPub
            OP_CHECKSIG
           ]

# This function provides the sigScript (aka input script) that can redeem the
# above transaction.  The parameters are the same as for P2PKH_scriptSig
# (), above.  You also will need to use the keys for alice, bob, and charlie,
# as well as your own key.  The private key parameter used is the global
# my_private_key.
def multisig_scriptSig(txin, txout, txin_scriptPubKey):
    bank_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, my_private_key)
    alice_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, alice_private_key)
    bob_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, bob_private_key)
    charlie_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, charlie_private_key)

    return [ 
            bank_sig, OP_0, alice_sig, bob_sig, OP_2
            ]

# The transaction hash received after successfully submitting the first
# transaction above (part 3a)
txid_multisig_txn1 = "82e2bf4e74f191920e0caf6bfedc6f588780fb50c7568fe171c30f33cebde9b0"

# The transaction hash received after successfully submitting the second
# transaction above (part 3b)
txid_multisig_txn2 = "c4d630fe4b1d063fb80b236b6803ec11558af6aec82eed59899b70878b0fb36c"


#------------------------------------------------------------
# Part 4: cross-chain transaction

# This is the API token obtained after creating an account on
# https://accounts.blockcypher.com/.  This is optional!  But you may want to
# keep it here so that everything is all in once place.
blockcypher_api_token = "5cf7769c5994405c9bf9d5d88de2d32c"

# These are the private keys and invoice addresses obtained on the BCY test
# network.
my_private_key_bcy_str = "2df10b7962d31a351cc3c7384a8eebc1d58b7062f92d22ed2961230efd144b44"
my_invoice_address_bcy_str = "BxMYnRnM1tZraeh4zJA2gJdhb6W8GK3LWt"
bob_private_key_bcy_str = "a2b5d51d3314b75d14058a2c68fea38793ad8ff569d7bfa8a9fd3c4e1d93eb4c"
bob_invoice_address_bcy_str = "CDsDvK8VuntgEVaGzBqabeFTHJkHMdXe3Q"

# This is the transaction hash for the funding transaction for Bob's BCY
# network wallet.
txid_bob_bcy_funding = "78eaed373256467452ee5e74a22ca72da533c33b10316e82980ca579293812e9"

# This is the transaction hash for the split transaction for the trasnaction
# above.
txid_bob_bcy_split = "6cf75e40899c5ca4dc18d8846c3c764bb1f28cfce606ae0dbbfce7bc6bd89c05"

# This is the secret used in this atomic swap.  It needs to be between 1 million
# and 2 billion.
atomic_swap_secret = 982345678

# This function provides the pubKey script (aka output script) that will set
# up the atomic swap.  This function is run by both Alice (aka you) and Bob,
# but on different networks (tBTC for you/Alice, and BCY for Bob).  This is
# used to create TXNs 1 and 3, which are described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.
def atomicswap_scriptPubKey(public_key_sender, public_key_recipient, hash_of_secret):
    return [ 
             OP_IF, #If redeem, 
             OP_HASH160,
             hash_of_secret,
             OP_EQUALVERIFY, #sigrecipient left on stack
             public_key_recipient,
             OP_CHECKSIG,
             OP_ELSE,
             OP_0,
             OP_ROT, OP_ROT, #0, sig_recipient, sig_sender
             OP_2,
             public_key_recipient,
             public_key_sender,
             OP_2,
             OP_CHECKMULTISIG,
             OP_ENDIF
           ]

# This is the ScriptSig that the receiver will use to redeem coins.  It's
# provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This creates the "normal" redeeming script, shown in steps 5 and 6 at 
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/atomicsteps.
def atomcswap_scriptSig_redeem(sig_recipient, secret):
    return [
        sig_recipient, secret, OP_TRUE,
    ]

# This is the ScriptSig for sending coins back to the sender if unredeemed; it
# is provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This is used to create TXNs 2 and 4, which are
# described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.  In
# practice, this would be time-locked in the future -- it would include a
# timestamp and call OP_CHECKLOCKTIMEVERIFY.  Because the time can not be
# known when the assignment is written, and as it will vary for each student,
# that part is omitted.
def atomcswap_scriptSig_refund(sig_sender, sig_recipient):
    return [
        sig_recipient, sig_sender, OP_FALSE,
    ]

# The transaction hash received after successfully submitting part 4a
txid_atomicswap_alice_send_tbtc = "001b42a3011c844e007a97b69aaed3bbba55d4affb30f0fdbccc007b17a014cd"

# The transaction hash received after successfully submitting part 4b
txid_atomicswap_bob_send_bcy = "211374b1521271a4217a6fb25164f46e40aa0c16182bd8f14d6c3b50cb6aeecd"

# The transaction hash received after successfully submitting part 4c
txid_atomicswap_alice_redeem_bcy = "b9586683bbdfa550e126bf5a9cc6c72fbe8a97ffddec3d2dbb3fd38b3578e9be"

# The transaction hash received after successfully submitting part 4d
txid_atomicswap_bob_redeem_tbtc = "336438e5d84632ba07bf53ae211feed959063c876db628df4e5bdbfe07091f76"


#------------------------------------------------------------
# part 5: return everything to the faucet

# nothing to fill in here, as we are going to look at the balance of
# `my_invoice_address_str` to verify that you've completed this part.