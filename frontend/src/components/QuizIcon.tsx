import React from 'react';
import {
    FaBook, FaGraduationCap, FaFlask, FaMicroscope, FaAtom, FaDna,
    FaCalculator, FaSquareRootAlt, FaInfinity, FaChartLine,
    FaGlobe, FaMapMarkedAlt, FaMountain, FaCompass,
    FaLandmark, FaScroll, FaTheaterMasks, FaMonument,
    FaPalette, FaMusic, FaGuitar, FaFilm,
    FaLanguage, FaBookOpen, FaQuoteRight, FaPenFancy,
    FaFootballBall, FaBasketballBall, FaTrophy, FaMedal,
    FaLeaf, FaTree, FaSeedling, FaBug,
    FaLaptopCode, FaRobot, FaMicrochip, FaProjectDiagram,
    FaHeart, FaBrain, FaUserMd, FaStethoscope,
    FaStar, FaRocket, FaCrown, FaGem,
    FaLightbulb, FaQuestionCircle, FaCheckCircle, FaExclamationCircle,
} from 'react-icons/fa';
import {
    GiAncientColumns, GiAncientRuins, GiAncientSword,
    GiEgyptianBird, GiGreekTemple, GiRomanToga,
    GiSpellBook, GiQuillInk,
    GiChemicalDrop, GiMaterialsScience, GiAtom, GiDna1,
    GiWorld, GiEarthAmerica, GiMountainRoad, GiVolcano,
} from 'react-icons/gi';
import {
    BsBook, BsJournalBookmark, BsNewspaper, BsPencil,
    BsMusicNoteBeamed, BsBrush, BsCamera, BsPalette,
} from 'react-icons/bs';
import { IconType } from 'react-icons';

const ICON_MAP: Record<string, IconType> = {
    'ancient-columns': GiAncientColumns,
    'ancient-ruins': GiAncientRuins,
    'sword': GiAncientSword,
    'egyptian': GiEgyptianBird,
    'temple': GiGreekTemple,
    'roman': GiRomanToga,
    'landmark': FaLandmark,
    'scroll': FaScroll,
    'monument': FaMonument,
    'theater': FaTheaterMasks,
    'flask': FaFlask,
    'microscope': FaMicroscope,
    'atom': FaAtom,
    'dna': FaDna,
    'chemical': GiChemicalDrop,
    'materials': GiMaterialsScience,
    'atom2': GiAtom,
    'dna2': GiDna1,
    'brain': FaBrain,
    'medicine': FaUserMd,
    'stethoscope': FaStethoscope,
    'heart': FaHeart,
    'calculator': FaCalculator,
    'sqrt': FaSquareRootAlt,
    'infinity': FaInfinity,
    'chart': FaChartLine,
    'globe': FaGlobe,
    'map': FaMapMarkedAlt,
    'mountain': FaMountain,
    'compass': FaCompass,
    'world': GiWorld,
    'earth': GiEarthAmerica,
    'mountain-road': GiMountainRoad,
    'volcano': GiVolcano,
    'language': FaLanguage,
    'book-open': FaBookOpen,
    'quote': FaQuoteRight,
    'pen': FaPenFancy,
    'spell-book': GiSpellBook,
    'quill': GiQuillInk,
    'book': BsBook,
    'journal': BsJournalBookmark,
    'newspaper': BsNewspaper,
    'pencil': BsPencil,
    'palette': FaPalette,
    'music': FaMusic,
    'guitar': FaGuitar,
    'film': FaFilm,
    'music-note': BsMusicNoteBeamed,
    'brush': BsBrush,
    'camera': BsCamera,
    'palette2': BsPalette,
    'football': FaFootballBall,
    'basketball': FaBasketballBall,
    'trophy': FaTrophy,
    'medal': FaMedal,
    'leaf': FaLeaf,
    'tree': FaTree,
    'seedling': FaSeedling,
    'bug': FaBug,
    'laptop': FaLaptopCode,
    'robot': FaRobot,
    'microchip': FaMicrochip,
    'diagram': FaProjectDiagram,
    'book-general': FaBook,
    'graduation': FaGraduationCap,
    'star': FaStar,
    'rocket': FaRocket,
    'crown': FaCrown,
    'gem': FaGem,
    'lightbulb': FaLightbulb,
    'question': FaQuestionCircle,
    'check': FaCheckCircle,
    'exclamation': FaExclamationCircle,
};

interface QuizIconProps {
    iconName: string;
    size?: number;
    className?: string;
}

export const QuizIcon: React.FC<QuizIconProps> = ({ iconName, size = 24, className = '' }) => {
    const Icon = ICON_MAP[iconName];

    if (!Icon) {
        // Fallback to book icon if not found
        return <FaBook size={size} className={className} />;
    }

    return <Icon size={size} className={className} />;
};
