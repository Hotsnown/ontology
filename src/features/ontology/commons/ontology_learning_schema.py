from dataclasses import dataclass, field
from typing import Set
from typing_extensions import Literal

import config.logging_config as logging_config


@dataclass
class CandidateTerm:
    """A Dataclass to contain Candidate terms informations.

    Parameters
    ----------
    value: str
        The candidate term string
    synonyms: Set[str]
        The candidate term sysnonyms strings
    hypernyms: Set[str]
        The candidate term hypernyms strings
    hyponyms: Set[str]
        The candidate term hyponyms strings
    antonyms: Set[str]
        The candidate term antonyms strings
    """
    value: str
    synonyms: Set[str] = field(default_factory=set)
    hypernyms: Set[str] = field(default_factory=set)
    hyponyms: Set[str] = field(default_factory=set)
    antonyms: Set[str] = field(default_factory=set)

    def __hash__(self):
        return hash(self.value)


@dataclass
class Concept:
    """Dataclass that contains concept information.

    Parameters
    ----------
    uid : str
        Concept unique id.
    terms : Set[str]
        Set of terms that is to say strings that represent the concept.
    external_uris: Set[str]
        Set of known URIs representing the concept in other KGs
    """
    uid: str
    terms: Set[str] = field(default_factory=set)
    external_uris: Set[str] = field(default_factory=set)

    def __post_init__(self):
        if not isinstance(self.uid, str):
            logging_config.logger.error(
                "Incompatible value type for Concept.uid attribute. It should be a str")

    def __hash__(self):
        return hash(self.uid)


@dataclass
class Relation:
    """Dataclass that contains relation information.

    Parameters
    ----------
    uid : str
        Relation unique id.
    source_concept_id : str
        UID of the relationship source.
    destination_concept_id : str
        UID of the relationship destination.
    terms : Set[str]
        Set of terms that is to say strings that represent the concept.
    """
    uid: str
    source_concept_id: str
    destination_concept_id: str
    terms: Set[str] = field(default_factory=set)

    def __post_init__(self):
        if not isinstance(self.uid, str):
            logging_config.logger.error(
                "Incompatible value type for Concept.uid attribute. It should be a str")

    def __hash__(self):
        return hash(self.uid)


MetaRelationType = Literal["generalisation", "related_to", "is_part_of"]


@dataclass
class MetaRelation:
    """Dataclass that contains meta-relation information.

    Parameters
    ----------
    uid : str
        Meta relation unique id.
    source_concept_id : str
        UID of the meta relationship source.
    destination_concept_id : str
        UID of the meta relationship destination.
    relation_type : MetaRelationType
        Type of the meta relation.
    """
    uid: str
    source_concept_id: str
    destination_concept_id: str
    relation_type: MetaRelationType

    def __post_init__(self):
        if not isinstance(self.uid, str):
            logging_config.logger.error(
                "Incompatible value type for Concept.uid attribute. It should be a str")

    def __hash__(self):
        return hash(self.uid)


@dataclass
class KR:
    """Dataclass that contains knowledge representation information.
    concepts : Set[Concept]
        Concepts contained in the knowledge representation.
    relations : Set[Relation]
        Relations contained in the knowledge representation.
    meta_relations : Set[MetaRelation]
        Meta relations contained in the knowlegde representation.
    """
    concepts: Set[Concept] = field(default_factory=set)
    relations: Set[Relation] = field(default_factory=set)
    meta_relations: Set[MetaRelation] = field(default_factory=set)
