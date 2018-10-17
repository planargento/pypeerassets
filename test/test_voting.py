import pytest
from typing import Iterator

from pypeerassets import voting
from pypeerassets.protocol import (Deck, IssueMode)
from pypeerassets.transactions import Transaction
from pypeerassets.provider import Explorer
from pypeerassets.pautils import find_tx_sender


deck = Deck(
    name="vote_deck",
    number_of_decimals=2,
    issue_mode=IssueMode.MULTI.value,
    network="ppc",
    production=True,
    version=1,
    id="7ee8026f5292f4953b741cc3259e1c66742a095e038642e09d6f22c2438b4467"
)


vote = voting.VoteInit.from_json({
    "deck": deck,
    "version": 1,
    "start_block": 1,
    "end_block": 100,
    "count_mode": 1,  # SIMPLE vote count method
    "choices": [
                "11",
                "3"],
    "description": "",
    "id": "0fce7f493038abb8aaa8f5b3e8130d01e5804c8dee9a19202c6cceae7c8e5e27",
    "vote_metainfo": b"https://imgur.com/my_pic.png"
})


def test_vote_tag():
    '''test deck vote tag creation'''

    assert voting.deck_vote_tag(deck).address == 'PFjDw9tJnCj3PExZPDUjY1fqFN1vtt8CUj'


def test_vote_init_object():

    vote_init = {
        "deck": deck,
        "version": 1,
        "start_block": 1,
        "end_block": 100,
        "count_mode": 1,  # SIMPLE vote count method
        "choices": [
                    "putin"
                    "merkel",
                    "trump"],
        "description": "test vote",
        "id": "0fce7f493038abb8aaa8f5b3e8130d01e5804c8dee9a19202c6cceae7c8e5e27",
        "vote_metainfo": b"https://imgur.com/my_logo.png"
    }

    vote = voting.VoteInit.from_json(vote_init)

    assert isinstance(vote, voting.VoteInit)

    assert isinstance(vote.metainfo_to_dict, dict)

    assert isinstance(vote.to_json(), dict)

    assert isinstance(str(vote), str)

    assert isinstance(vote.metainfo_to_protobuf, bytes)


def test_parse_vote_info():
    '''test parsing vote metainfo from the OP_RETURN'''

    protobuf = b'\x08\x01\x12\x0cmy test vote\x18\xf9\x87\x16 \xe1\x8f\x16(\x012\x02no2\x03yes2\x05maybe'

    vote = voting.parse_vote_init(protobuf)

    assert isinstance(vote, dict)

    assert vote == {'choices': ['no', 'yes', 'maybe'],
                    'count_mode': 'SIMPLE',
                    'description': 'my test vote',
                    'end_block': 362465,
                    'start_block': 361465,
                    'version': 1,
                    'vote_metainfo': b''}


def test_vote_init():

    provider = Explorer(network='tppc')
    inputs = provider.select_inputs("msnHPXDWuJhRBPVNQnwXdKvEMQHLr9z1P5", 0.02)
    change_address = "msnHPXDWuJhRBPVNQnwXdKvEMQHLr9z1P5"

    my_deck = deck
    my_deck.network = "tppc"

    vote_init = voting.vote_init(vote, inputs, change_address)

    assert isinstance(vote_init, Transaction)


def test_find_vote_inits():
    '''test finding and parsing vote inits for <deck>'''

    expected_vote_init = "6382bf31a3f8e288afd6a981e09d621d0f1bd8319cbf9657d7b332072ceffdc8"
    provider = Explorer(network='tppc')

    inits = list(voting.find_vote_inits(provider, deck))

    assert isinstance(inits[0], voting.VoteInit)
    assert inits[0].id == expected_vote_init


def test_vote_cast():
    '''test casting a vote'''

    provider = Explorer(network='tppc')
    inputs = provider.select_inputs("msnHPXDWuJhRBPVNQnwXdKvEMQHLr9z1P5", 0.02)
    change_address = "msnHPXDWuJhRBPVNQnwXdKvEMQHLr9z1P5"

    my_deck = deck
    my_deck.network = "tppc"

    cast = voting.vote_cast(vote=vote,
                            choice_index=0,
                            inputs=inputs,
                            change_address=change_address)

    assert isinstance(cast, Transaction)


def test_vote_object():

    provider = Explorer(network='tppc')

    raw_tx = provider.getrawtransaction('a2328f95d50261438cf4184119d84337a86cce9000e71255cbf36dbcd5c06096', 1)
    sender = find_tx_sender(provider, raw_tx)
    confirmations = raw_tx["confirmations"]
    blocknum = provider.getblock(raw_tx["blockhash"])["height"]

    v = voting.Vote(vote_init=vote,
                    id=raw_tx['txid'],
                    sender=sender,
                    blocknum=blocknum,
                    confirmations=confirmations,
                    timestamp=raw_tx["blocktime"]
                    )

    assert isinstance(v, voting.Vote)
    assert not v.is_valid


def test_find_casts():

    provider = Explorer(network='tppc')

    my_vote = vote
    my_vote.deck.network = 'tppc'

    casts = voting.find_vote_casts(provider, vote, 0)

    assert isinstance(casts, Iterator)
    assert isinstance(next(casts), voting.Vote)