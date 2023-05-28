from typing import TypedDict


class MediaFormats(TypedDict):
    """Media formats"""

    media_format: str
    tv: str
    tv_short: str
    movie: str
    special: str
    ova: str
    ona: str
    music: str
    manga: str
    novel: str
    manhua: str
    manhwa: str
    doujin: str
    one_shot: str


class Season(TypedDict):
    """Seasons"""

    winter: str
    spring: str
    summer: str
    fall: str
    unknown: str


class Year(TypedDict):
    """Year"""

    unknown: str


class CommonSearch(TypedDict):
    """Search Context"""

    init_title: str
    """Title when search is initialized"""
    init: str
    """Description when search is initialized"""
    result_title: str
    """Title when search found results"""
    result: str
    """Description when search found results"""
    no_result: str
    """Description when search found no results"""


class Commons(TypedDict):
    """Common Context"""

    unknown: str
    """Unknown"""
    none: str
    """None"""
    error: str
    """Error"""
    reason: str
    """Reason"""
    search: CommonSearch
    """Search Context"""
    media_formats: MediaFormats
    """Media formats"""
    season: Season
    """Seasons"""
    year: Year
    """Year"""


class CommonQuantity(TypedDict):
    """Quantity Context"""

    one: str
    """Description when quantity is 1"""
    two: str
    """Description when quantity is 2"""
    many: str
    """Description when quantity is more than 2"""


class Quantities(TypedDict):
    """Quantities Context"""

    anime: CommonQuantity
    """Anime Quantity Context"""
    manga: CommonQuantity
    """Manga Quantity Context"""
    games: CommonQuantity
    """Games Quantity Context"""
    shows: CommonQuantity
    """Shows Quantity Context"""
    movies: CommonQuantity
    """Movies Quantity Context"""
    tracks: CommonQuantity
    """Tracks Quantity Context"""
    albums: CommonQuantity
    """Albums Quantity Context"""
    artists: CommonQuantity
    """Artists Quantity Context"""
    years: CommonQuantity
    """Years Quantity Context"""
    months: CommonQuantity
    """Months Quantity Context"""
    days: CommonQuantity
    """Days Quantity Context"""
    hours: CommonQuantity
    """Hours Quantity Context"""
    minutes: CommonQuantity
    """Minutes Quantity Context"""


class Genres(TypedDict):
    """Genres Context"""

    _yon_koma: str
    """4-Koma"""
    achromatic: str
    """Achromatic"""
    achronological_order: str
    """Achronological Order"""
    acting: str
    """Acting"""
    action: str
    """Action"""
    adoption: str
    """Adoption"""
    adventure: str
    """Adventure"""
    advertisement: str
    """Advertisement"""
    afterlife: str
    """Afterlife"""
    age_gap: str
    """Age Gap"""
    age_regression: str
    """Age Regression"""
    agender: str
    """Agender"""
    agriculture: str
    """Agriculture"""
    airsoft: str
    """Airsoft"""
    alchemy: str
    """Alchemy"""
    aliens: str
    """Aliens"""
    alternate_universe: str
    """Alternate Universe"""
    american_football: str
    """American Football"""
    amnesia: str
    """Amnesia"""
    anachronism: str
    """Anachronism"""
    angels: str
    """Angels"""
    animals: str
    """Animals"""
    anthology: str
    """Anthology"""
    anthropomorphic: str
    """Anthropomorphic"""
    anti_hero: str
    """Anti-Hero"""
    archery: str
    """Archery"""
    artificial_intelligence: str
    """Artificial Intelligence"""
    asexual: str
    """Asexual"""
    assassins: str
    """Assassins"""
    astronomy: str
    """Astronomy"""
    athletics: str
    """Athletics"""
    augmented_reality: str
    """Augmented Reality"""
    autobiographical: str
    """Autobiographical"""
    aviation: str
    """Aviation"""
    award_winning: str
    """Award Winning"""
    badminton: str
    """Badminton"""
    band: str
    """Band"""
    bar: str
    """Bar"""
    baseball: str
    """Baseball"""
    basketball: str
    """Basketball"""
    battle_royale: str
    """Battle Royale"""
    biographical: str
    """Biographical"""
    bisexual: str
    """Bisexual"""
    body_horror: str
    """Body Horror"""
    body_swapping: str
    """Body Swapping"""
    boxing: str
    """Boxing"""
    boys_love: str
    """Boys' Love"""
    bullying: str
    """Bullying"""
    butler: str
    """Butler"""
    calligraphy: str
    """Calligraphy"""
    cannibalism: str
    """Cannibalism"""
    card_battle: str
    """Card Battle"""
    cars: str
    """Cars"""
    centaur: str
    """Centaur"""
    cgi: str
    """CGI"""
    cheerleading: str
    """Cheerleading"""
    chibi: str
    """Chibi"""
    childcare: str
    """Childcare"""
    chimera: str
    """Chimera"""
    chuunibyou: str
    """Chuunibyou"""
    circus: str
    """Circus"""
    classic_literature: str
    """Classic Literature"""
    clone: str
    """Clone"""
    college: str
    """College"""
    combat_sports: str
    """Combat Sports"""
    comedy: str
    """Comedy"""
    coming_of_age: str
    """Coming of Age"""
    conspiracy: str
    """Conspiracy"""
    cosmic_horror: str
    """Cosmic Horror"""
    cosplay: str
    """Cosplay"""
    crime: str
    """Crime"""
    crossdressing: str
    """Crossdressing"""
    crossover: str
    """Crossover"""
    cult: str
    """Cult"""
    cultivation: str
    """Cultivation"""
    cute_boys_doing_cute_things: str
    """Cute Boys Doing Cute Things"""
    cute_girls_doing_cute_things: str
    """Cute Girls Doing Cute Things"""
    cyberpunk: str
    """Cyberpunk"""
    cyborg: str
    """Cyborg"""
    cycling: str
    """Cycling"""
    dancing: str
    """Dancing"""
    death_game: str
    """Death Game"""
    delinquents: str
    """Delinquents"""
    demons: str
    """Demons"""
    denpa: str
    """Denpa"""
    desert: str
    """Desert"""
    detective: str
    """Detective"""
    dinosaurs: str
    """Dinosaurs"""
    disability: str
    """Disability"""
    dissociative_identities: str
    """Dissociative Identities"""
    dragons: str
    """Dragons"""
    drama: str
    """Drama"""
    drawing: str
    """Drawing"""
    drugs: str
    """Drugs"""
    dullahan: str
    """Dullahan"""
    dungeon: str
    """Dungeon"""
    dystopian: str
    """Dystopian"""
    e_sports: str
    """E-Sports"""
    ecchi: str
    """Ecchi"""
    economics: str
    """Economics"""
    educational: str
    """Educational"""
    elf: str
    """Elf"""
    ensemble_cast: str
    """Ensemble Cast"""
    environmental: str
    """Environmental"""
    episodic: str
    """Episodic"""
    ero_guro: str
    """Ero Guro"""
    erotica: str
    """Erotica"""
    espionage: str
    """Espionage"""
    fairy_tale: str
    """Fairy Tale"""
    fairy: str
    """Fairy"""
    family_life: str
    """Family Life"""
    fantasy: str
    """Fantasy"""
    fashion: str
    """Fashion"""
    female_harem: str
    """Female Harem"""
    female_protagonist: str
    """Female Protagonist"""
    femboy: str
    """Femboy"""
    fencing: str
    """Fencing"""
    firefighters: str
    """Firefighters"""
    fishing: str
    """Fishing"""
    fitness: str
    """Fitness"""
    flash: str
    """Flash"""
    food: str
    """Food"""
    football: str
    """Football"""
    foreign: str
    """Foreign"""
    found_family: str
    """Found Family"""
    fugitive: str
    """Fugitive"""
    full_cgi: str
    """Full CGI"""
    full_color: str
    """Full Color"""
    gag_humor: str
    """Gag Humor"""
    gambling: str
    """Gambling"""
    gangs: str
    """Gangs"""
    gender_bending: str
    """Gender Bending"""
    ghost: str
    """Ghost"""
    girls_love: str
    """Girls' Love"""
    go: str
    """Go"""
    goblin: str
    """Goblin"""
    gods: str
    """Gods"""
    golf: str
    """Golf"""
    gore: str
    """Gore"""
    gourmet: str
    """Gourmet"""
    gyaru: str
    """Gyaru"""
    handball: str
    """Handball"""
    harem: str
    """Harem"""
    henshin: str
    """Henshin"""
    heterosexual: str
    """Heterosexual"""
    high_stakes_game: str
    """High Stakes Game"""
    hikikomori: str
    """Hikikomori"""
    historical: str
    """Historical"""
    homeless: str
    """Homeless"""
    horror: str
    """Horror"""
    ice_skating: str
    """Ice Skating"""
    idol: str
    """Idol"""
    idols_female: str
    """Idol (Female)"""
    idols_male: str
    """Idol (Male)"""
    isekai: str
    """Isekai"""
    iyashikei: str
    """Iyashikei"""
    josei: str
    """Josei"""
    judo: str
    """Judo"""
    kaiju: str
    """Kaiju"""
    karuta: str
    """Karuta"""
    kemonomimi: str
    """Kemonomimi"""
    kids: str
    """Kids"""
    kuudere: str
    """Kuudere"""
    lacrosse: str
    """Lacrosse"""
    language_barrier: str
    """Language Barrier"""
    lgbtq_themes: str
    """LGBTQ+ Themes"""
    lost_civilization: str
    """Lost Civilization"""
    love_polygon: str
    """Love Polygon"""
    love_triangle: str
    """Love Triangle"""
    mafia: str
    """Mafia"""
    magic: str
    """Magic"""
    magical_sex_shift: str
    """Magical Sex Shift"""
    mahjong: str
    """Mahjong"""
    mahou_shoujo: str
    """Mahou Shoujo"""
    maids: str
    """Maids"""
    makeup: str
    """Makeup"""
    male_harem: str
    """Male Harem"""
    male_protagonist: str
    """Male Protagonist"""
    marriage: str
    """Marriage"""
    martial_arts: str
    """Martial Arts"""
    mecha: str
    """Mecha"""
    medical: str
    """Medical"""
    memory_manipulation: str
    """Memory Manipulation"""
    mermaid: str
    """Mermaid"""
    meta: str
    """Meta"""
    military: str
    """Military"""
    mixed_gender_harem: str
    """Mixed Gender Harem"""
    monster_boy: str
    """Monster Boy"""
    monster_girl: str
    """Monster Girl"""
    mopeds: str
    """Mopeds"""
    motorcycles: str
    """Motorcycles"""
    music: str
    """Music"""
    musical: str
    """Musical"""
    mystery: str
    """Mystery"""
    mythology: str
    """Mythology"""
    necromancy: str
    """Necromancy"""
    nekomimi: str
    """Nekomimi"""
    ninja: str
    """Ninja"""
    no_dialogue: str
    """No Dialogue"""
    noir: str
    """Noir"""
    non_fiction: str
    """Non-fiction"""
    nudity: str
    """Nudity"""
    nun: str
    """Nun"""
    office_lady: str
    """Office Lady"""
    oiran: str
    """Oiran"""
    ojou_sama: str
    """Ojou-sama"""
    organized_crime: str
    """Organized Crime"""
    orphan: str
    """Orphan"""
    otaku_culture: str
    """Otaku Culture"""
    outdoor: str
    """Outdoor"""
    pandemic: str
    """Pandemic"""
    parkour: str
    """Parkour"""
    parody: str
    """Parody"""
    performing_arts: str
    """Performing Arts"""
    pets: str
    """Pets"""
    philosophy: str
    """Philosophy"""
    photography: str
    """Photography"""
    pirates: str
    """Pirates"""
    poker: str
    """Poker"""
    police: str
    """Police"""
    politics: str
    """Politics"""
    post_apocalyptic: str
    """Post-Apocalyptic"""
    pov: str
    """POV"""
    primarily_adult_cast: str
    """Primarily Adult Cast"""
    primarily_child_cast: str
    """Primarily Child Cast"""
    primarily_female_cast: str
    """Primarily Female Cast"""
    primarily_male_cast: str
    """Primarily Male Cast"""
    primarily_teen_cast: str
    """Primarily Teen Cast"""
    prison: str
    """Prison"""
    psychological: str
    """Psychological"""
    puppetry: str
    """Puppetry"""
    racing: str
    """Racing"""
    rakugo: str
    """Rakugo"""
    real_robot: str
    """Real Robot"""
    rehabilitation: str
    """Rehabilitation"""
    reincarnation: str
    """Reincarnation"""
    religion: str
    """Religion"""
    revenge: str
    """Revenge"""
    reverse_harem: str
    """Reverse Harem"""
    robots: str
    """Robots"""
    romance: str
    """Romance"""
    romantic_subtext: str
    """Romantic Subtext"""
    rotoscoping: str
    """Rotoscoping"""
    rugby: str
    """Rugby"""
    rural: str
    """Rural"""
    samurai: str
    """Samurai"""
    satire: str
    """Satire"""
    school_club: str
    """School Club"""
    school: str
    """School"""
    sci_fi: str
    """Sci-Fi"""
    scuba_diving: str
    """Scuba Diving"""
    seinen: str
    """Seinen"""
    shapeshifting: str
    """Shapeshifting"""
    ships: str
    """Ships"""
    shogi: str
    """Shogi"""
    shoujo: str
    """Shoujo"""
    shounen: str
    """Shounen"""
    showbiz: str
    """Showbiz"""
    shrine_maiden: str
    """Shrine Maiden"""
    skateboarding: str
    """Skateboarding"""
    skeleton: str
    """Skeleton"""
    slapstick: str
    """Slapstick"""
    slavery: str
    """Slavery"""
    slice_of_life: str
    """Slice of Life"""
    software_development: str
    """Software Development"""
    space_opera: str
    """Space Opera"""
    space: str
    """Space"""
    spearplay: str
    """Spearplay"""
    sports: str
    """Sports"""
    steampunk: str
    """Steampunk"""
    stop_motion: str
    """Stop Motion"""
    strategy_game: str
    """Strategy Game"""
    succubus: str
    """Succubus"""
    suicide: str
    """Suicide"""
    sumo: str
    """Sumo"""
    super_power: str
    """Super Power"""
    super_robot: str
    """Super Robot"""
    superhero: str
    """Superhero"""
    supernatural: str
    """Supernatural"""
    surfing: str
    """Surfing"""
    surreal_comedy: str
    """Surreal Comedy"""
    survival: str
    """Survival"""
    suspense: str
    """Suspense"""
    swimming: str
    """Swimming"""
    swordplay: str
    """Swordplay"""
    table_tennis: str
    """Table Tennis"""
    tanks: str
    """Tanks"""
    tanned_skin: str
    """Tanned Skin"""
    teacher: str
    """Teacher"""
    team_sports: str
    """Team Sports"""
    teens_love: str
    """Teens' Love"""
    tennis: str
    """Tennis"""
    terrorism: str
    """Terrorism"""
    thriller: str
    """Thriller"""
    time_manipulation: str
    """Time Manipulation"""
    time_skip: str
    """Time Skip"""
    time_travel: str
    """Time Travel"""
    tokusatsu: str
    """Tokusatsu"""
    tomboy: str
    """Tomboy"""
    torture: str
    """Torture"""
    tragedy: str
    """Tragedy"""
    trains: str
    """Trains"""
    transgender: str
    """Transgender"""
    travel: str
    """Travel"""
    triads: str
    """Triads"""
    tsundere: str
    """Tsundere"""
    twins: str
    """Twins"""
    urban_fantasy: str
    """Urban Fantasy"""
    urban: str
    """Urban"""
    vampire: str
    """Vampire"""
    video_game: str
    """Video Game"""
    vikings: str
    """Vikings"""
    villainess: str
    """Villainess"""
    virtual_world: str
    """Virtual World"""
    visual_arts: str
    """Visual Arts"""
    volleyball: str
    """Volleyball"""
    vtuber: str
    """VTuber"""
    war: str
    """War"""
    werewolf: str
    """Werewolf"""
    witch: str
    """Witch"""
    work: str
    """Work"""
    workplace: str
    """Workplace"""
    wrestling: str
    """Wrestling"""
    writing: str
    """Writing"""
    wuxia: str
    """Wuxia"""
    yakuza: str
    """Yakuza"""
    yandere: str
    """Yandere"""
    youkai: str
    """Youkai"""
    yuri: str
    """Yuri"""
    zombie: str
    """Zombie"""


class AboutCommand(TypedDict):
    """About Command"""

    text: str
    """Text"""


class CommonPingCommandFields(TypedDict):
    """Common Ping Command Fields"""

    title: str
    """Title"""
    text: str
    """Text"""


class PingCommand(TypedDict):
    """Ping Command"""

    ping: CommonPingCommandFields
    """Ping"""
    pong: CommonPingCommandFields
    """Pong"""
    bot: CommonPingCommandFields
    """Message timestamp comparison"""
    websocket: CommonPingCommandFields
    """Discord Websocket"""
    dbRead: CommonPingCommandFields
    """Database Read"""
    langRead: CommonPingCommandFields
    """Language Read"""
    pyTime: CommonPingCommandFields
    """Python Time"""
    uptime: CommonPingCommandFields
    """Uptime"""


class CommonTitleValue(TypedDict):
    """Common Invite Command Fields"""

    title: str
    """Title"""
    value: str
    """Value"""


class InviteCommandFields(TypedDict):
    """Invite Command Fields"""

    acc: CommonTitleValue
    """Required Permissions Access"""
    scope: CommonTitleValue
    """Bot Scope"""


class InviteButtons(TypedDict):
    """Invite Buttons"""

    invite: str
    """Invite"""
    support: str
    """Support"""


class InviteCommand(TypedDict):
    """Invite Command"""

    title: str
    """Title"""
    text: str
    """Text"""
    fields: InviteCommandFields
    """Fields"""
    buttons: InviteButtons
    """Buttons"""


class PrivacyCommand(TypedDict):
    """Privacy Command"""

    title: str
    """Title"""
    read: str
    """Read"""
    text: str
    """Text"""


class SupportCommand(TypedDict):
    """Support Command"""

    title: str
    """Title"""
    text: str
    """Text"""


class RandomNekomimiCommand(TypedDict):
    """Random Nekomimi Command"""

    author: str
    """Platform"""
    source: CommonTitleValue
    """Source"""
    artist: str
    """Artist"""


class RandomCommand(TypedDict):
    """Random Command"""

    nekomimi: RandomNekomimiCommand
    """Nekomimi"""


class AnimeExceptions(TypedDict):
    """Anime Exceptions"""

    title: str
    """Title"""
    text: str
    """Text"""
    footer: str
    """Footer"""


class AnimeSearchCommand(TypedDict):
    """Anime Search Command"""

    exceptions: AnimeExceptions
    """Exceptions"""


class AnimeCommand(TypedDict):
    """Anime Command"""

    search: AnimeSearchCommand
    """Search"""


class ProfileCommons(TypedDict):
    """Profile Commons"""

    about: str
    """About"""
    username: str
    """Username"""
    nickname: str
    """Nickname"""
    realname: str
    """Real Name"""
    default: str
    """Default"""
    bot: str
    """Bot Status"""


class ProfileExceptions(TypedDict):
    """Profile Exceptions"""

    general: str
    """General Exception"""
    unknown: str
    """Unknown User Exception"""


class ProfileDiscordCommand(TypedDict):
    """Profile Discord Command"""

    title: str
    """Title"""
    snowflake: str
    """Snowflake"""
    joined_discord: str
    """Joined Discord"""
    joined_server: str
    """Joined Server"""
    boost_status: str
    """Boost Status"""
    boost_since: str
    """Boost Since"""
    not_boosting: str
    """Not Boosting"""
    registered: str
    """Registered status"""
    display_name: str
    """Display Name"""


class ProfileLastfmCommand(TypedDict):
    """Profile Lastfm Command"""

    created: str
    """Created"""
    total_scrobbles: str
    """Total Scrobbles"""
    curr_playing: str
    """Currently Playing"""
    link: str
    """Link"""


class ProfileCommand(TypedDict):
    """Profile Command"""

    commons: ProfileCommons
    """Commons"""
    exceptions: ProfileExceptions
    """Exceptions"""
    discord: ProfileDiscordCommand
    """Discord"""
    lastfm: ProfileLastfmCommand
    """Lastfm"""


class UtilityCommons(TypedDict):
    """Common strings for utility commands"""

    result: str
    """Result"""
    string: str
    """String"""


class BaseUtilityCommand(TypedDict):
    """Base utility command"""

    exception: str
    """Exception"""


class UtilityMathCommand(BaseUtilityCommand):
    """Utility math command"""

    expression: str
    """Expression"""


class UtilityBase64Command(BaseUtilityCommand):
    """Utility base64 command"""


class UtilityColorCommand(BaseUtilityCommand):
    """Utility color command"""

    color: str
    """Color"""
    name: str
    """Name of the color"""
    powered: str
    """Attribution"""


class UtilityQRCommand(BaseUtilityCommand):
    """Utility QR command"""

    powered: str
    """Attribution"""


class UtilitySnoflakeCommand(TypedDict):
    """Utility snoflake command"""

    snowflake: str
    """Snowflake"""
    title: str
    """Title"""
    text: str
    """Text"""
    timestamp: str
    """Timestamp"""
    date: str
    """Date"""
    full_date: str
    """Full Date"""
    relative: str
    """Relative"""


class UtilityCommand(TypedDict):
    """Utility Command"""

    commons: UtilityCommons
    """Commons"""
    math: UtilityMathCommand
    """Math"""
    base64: UtilityBase64Command
    """Base64"""
    color: UtilityColorCommand
    """Color"""
    qrcode: UtilityQRCommand
    """QR"""
    snoflake: UtilitySnoflakeCommand
    """Snoflake"""


class Strings(TypedDict):
    """Strings"""

    about: AboutCommand
    """About Command"""
    ping: PingCommand
    """Ping Command"""
    invite: InviteCommand
    """Invite Command"""
    privacy: PrivacyCommand
    """Privacy Command"""
    support: SupportCommand
    """Support Command"""
    random: RandomCommand
    """Random Command"""
    anime: AnimeCommand
    """Anime Command"""
    profile: ProfileCommand
    """Profile Command"""
    utility: UtilityCommand
    """Utility Command"""


class LanguageDict(TypedDict):
    """Type annotation for language dict"""

    commons: Commons
    """Commons"""
    quantities: Quantities
    """Quantities"""
    genres: Genres
    """Genres"""
    strings: Strings
    """Strings"""
