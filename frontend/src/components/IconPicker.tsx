import React, { useState } from 'react';
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
    GiAncientColumns, GiAncientRuins, GiVase, GiAncientSword,
    GiEgyptianBird, GiPyramids, GiGreekTemple, GiRomanToga,
    GiSpellBook, GiCrystalBall, GiScrollUnfurled, GiQuillInk,
    GiChemicalDrop, GiMaterialsScience, GiAtom, GiDna1,
    GiWorld, GiEarthAmerica, GiMountainRoad, GiVolcano,
} from 'react-icons/gi';
import {
    BsBook, BsJournalBookmark, BsNewspaper, BsPencil,
    BsMusicNoteBeamed, BsBrush, BsCamera, BsPalette,
} from 'react-icons/bs';
import { IconType } from 'react-icons';
import './IconPicker.css';

interface IconPickerProps {
    onSelect: (icon: string) => void;
    onClose: () => void;
}

interface IconCategory {
    name: string;
    icons: { icon: IconType; name: string }[];
}

const ICON_CATEGORIES: IconCategory[] = [
    {
        name: '📜 Historia',
        icons: [
            { icon: GiAncientColumns, name: 'ancient-columns' },
            { icon: GiAncientRuins, name: 'ancient-ruins' },
            { icon: GiVase, name: 'vase' },
            { icon: GiAncientSword, name: 'sword' },
            { icon: GiEgyptianBird, name: 'egyptian' },
            { icon: GiPyramids, name: 'pyramids' },
            { icon: GiGreekTemple, name: 'temple' },
            { icon: GiRomanToga, name: 'roman' },
            { icon: FaLandmark, name: 'landmark' },
            { icon: FaScroll, name: 'scroll' },
            { icon: FaMonument, name: 'monument' },
            { icon: FaTheaterMasks, name: 'theater' },
        ],
    },
    {
        name: '🔬 Nauki ścisłe',
        icons: [
            { icon: FaFlask, name: 'flask' },
            { icon: FaMicroscope, name: 'microscope' },
            { icon: FaAtom, name: 'atom' },
            { icon: FaDna, name: 'dna' },
            { icon: GiChemicalDrop, name: 'chemical' },
            { icon: GiMaterialsScience, name: 'materials' },
            { icon: GiAtom, name: 'atom2' },
            { icon: GiDna1, name: 'dna2' },
            { icon: FaBrain, name: 'brain' },
            { icon: FaUserMd, name: 'medicine' },
            { icon: FaStethoscope, name: 'stethoscope' },
            { icon: FaHeart, name: 'heart' },
        ],
    },
    {
        name: '📐 Matematyka',
        icons: [
            { icon: FaCalculator, name: 'calculator' },
            { icon: FaSquareRootAlt, name: 'sqrt' },
            { icon: FaInfinity, name: 'infinity' },
            { icon: FaChartLine, name: 'chart' },
        ],
    },
    {
        name: '🌍 Geografia',
        icons: [
            { icon: FaGlobe, name: 'globe' },
            { icon: FaMapMarkedAlt, name: 'map' },
            { icon: FaMountain, name: 'mountain' },
            { icon: FaCompass, name: 'compass' },
            { icon: GiWorld, name: 'world' },
            { icon: GiEarthAmerica, name: 'earth' },
            { icon: GiMountainRoad, name: 'mountain-road' },
            { icon: GiVolcano, name: 'volcano' },
        ],
    },
    {
        name: '📚 Języki',
        icons: [
            { icon: FaLanguage, name: 'language' },
            { icon: FaBookOpen, name: 'book-open' },
            { icon: FaQuoteRight, name: 'quote' },
            { icon: FaPenFancy, name: 'pen' },
            { icon: GiSpellBook, name: 'spell-book' },
            { icon: GiQuillInk, name: 'quill' },
            { icon: BsBook, name: 'book' },
            { icon: BsJournalBookmark, name: 'journal' },
            { icon: BsNewspaper, name: 'newspaper' },
            { icon: BsPencil, name: 'pencil' },
        ],
    },
    {
        name: '🎨 Sztuka',
        icons: [
            { icon: FaPalette, name: 'palette' },
            { icon: FaMusic, name: 'music' },
            { icon: FaGuitar, name: 'guitar' },
            { icon: FaFilm, name: 'film' },
            { icon: BsMusicNoteBeamed, name: 'music-note' },
            { icon: BsBrush, name: 'brush' },
            { icon: BsCamera, name: 'camera' },
            { icon: BsPalette, name: 'palette2' },
        ],
    },
    {
        name: '⚽ Sport',
        icons: [
            { icon: FaFootballBall, name: 'football' },
            { icon: FaBasketballBall, name: 'basketball' },
            { icon: FaTrophy, name: 'trophy' },
            { icon: FaMedal, name: 'medal' },
        ],
    },
    {
        name: '🌱 Przyroda',
        icons: [
            { icon: FaLeaf, name: 'leaf' },
            { icon: FaTree, name: 'tree' },
            { icon: FaSeedling, name: 'seedling' },
            { icon: FaBug, name: 'bug' },
        ],
    },
    {
        name: '💻 Technologia',
        icons: [
            { icon: FaLaptopCode, name: 'laptop' },
            { icon: FaRobot, name: 'robot' },
            { icon: FaMicrochip, name: 'microchip' },
            { icon: FaProjectDiagram, name: 'diagram' },
        ],
    },
    {
        name: '🎓 Ogólne',
        icons: [
            { icon: FaBook, name: 'book-general' },
            { icon: FaGraduationCap, name: 'graduation' },
            { icon: FaStar, name: 'star' },
            { icon: FaRocket, name: 'rocket' },
            { icon: FaCrown, name: 'crown' },
            { icon: FaGem, name: 'gem' },
            { icon: FaLightbulb, name: 'lightbulb' },
            { icon: FaQuestionCircle, name: 'question' },
            { icon: FaCheckCircle, name: 'check' },
            { icon: FaExclamationCircle, name: 'exclamation' },
        ],
    },
];

export const IconPicker: React.FC<IconPickerProps> = ({ onSelect, onClose }) => {
    const [selectedCategory, setSelectedCategory] = useState(0);

    const handleIconClick = (iconName: string) => {
        onSelect(iconName);
    };

    return (
        <div className="icon-picker">
            <div className="icon-picker-header">
                <h3>Wybierz ikonę</h3>
                <button type="button" className="icon-picker-close" onClick={onClose}>✕</button>
            </div>

            <div className="icon-picker-categories">
                {ICON_CATEGORIES.map((category, index) => (
                    <button
                        key={index}
                        type="button"
                        className={`category-button ${selectedCategory === index ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(index)}
                    >
                        {category.name}
                    </button>
                ))}
            </div>

            <div className="icon-picker-grid">
                {ICON_CATEGORIES[selectedCategory].icons.map(({ icon: Icon, name }) => (
                    <button
                        key={name}
                        type="button"
                        className="icon-button"
                        onClick={() => handleIconClick(name)}
                        title={name}
                    >
                        <Icon size={32} />
                    </button>
                ))}
            </div>
        </div>
    );
};
