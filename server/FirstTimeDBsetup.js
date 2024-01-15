
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Email VARCHAR(255),
    DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  
  CREATE TABLE GameStats (
    StatsID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    GamesPlayed INT DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
  );
  
  CREATE TABLE IndividualGames (
    GameID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    TimeTaken INT,
    OptimalityScore INT,
    NumberOfMoves INT,
    MovesPerSecond INT,
    HintsUsed INT,
    OptimalSolutionLength INT,
    SolutionShown BOOLEAN,
    IncorrectMoves INT,
    GameDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    MazeType VARCHAR(255),
    MazeWidth INT,
    MazeHeight INT,
    GenerationAlgorithm VARCHAR(255),
    SolvingAlgorithm VARCHAR(255),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
  );